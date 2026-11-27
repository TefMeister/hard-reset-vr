"""Hard Reset VR: Tefa's skinned Meshy glove -> the add-on's game file (.hrsk) and its colour texture (.tga).
2026-11-27 (/pd). Run headless, never on the open Blender:
    blender -b meshy_hand_<side>_skinned.blend -P glove_export.py -- [centre=circle|room] <side> <out folder> <faces> [<faces> ...]
side = right | left. Each <faces> count is slimmed, capped at 4 bones per point, normalised and measured with Skin
Checker (grip, trigger finger out, fist) beside the full glove; the LAST count given is the one written out.

What it writes (out folder):
  hand_<side>.hrsk       the slimmed glove: points (position, normal, UV, 4 bones + weights), triangles, the 16 bones'
                         rest frames and each bone's full-curl angle; in the OpenXR GRIP frame (see grip_frame())
  hand_<side>.tga        the base colour texture, 1024 x 1024, 24-bit, uncompressed, bottom row first
  hand_<side>_golden.bin Blender's own bent points (Armature, Preserve Volume) for the grip and fist poses, per game
                         point, in the same frame: test/hr_hands_skin_test.c checks our C skinning against them
  hand_<side>_report.json every measurement
  meshy_hand_<side>_game.blend (beside the source .blend): the slimmed glove, for Tefa to look at
The source .blend is never saved over.

File layout (little-endian), version 1:
  header  char magic[4] "HRSK"; u32 version; u32 n_bones; u32 n_verts; u32 n_idx; u32 side (0 left, 1 right);
          f32 grip_centre[3] (where the grip origin sits in the source .blend, for the record); f32 tube_radius_m
  bone    char name[16]; i32 parent (-1 = root; always before the bone); f32 rest[12] (3 rows of R | t, column vectors:
          p_frame = R p_bone + t; Blender's bone matrix_local taken into the grip frame); f32 curl_max_deg
  vertex  f32 p[3]; f32 n[3]; f32 uv[2] (Blender's: v up); u8 bone[4]; f32 w[4] (sum 1; unused slots weight 0)
  index   u32[n_idx], triangles
Golden: char magic[4] "HRSG"; u32 n_verts; u32 n_poses; then per pose: f32 deg[15] (thumb, index, middle, ring,
pinky x segments 1..3), f32 p[n_verts][3].
"""
import bpy, sys, os, json, struct, math
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
CENTRE = 'circle'
if argv and argv[0].startswith("centre="):
    CENTRE = argv.pop(0).split("=", 1)[1]           # circle (the fitted tube centre) | room (the roomiest spot near it)
CLEAR_SEARCH_M = 0.025
SIDE, OUT, FACES = argv[0].lower(), argv[1], [int(x) for x in argv[2:]]
assert SIDE in ("left", "right") and FACES
os.makedirs(OUT, exist_ok=True)
L = "R" if SIDE == "right" else "L"
MESH, RIG = f"{L} glove skinned", f"HandRig_{L}"
FINGERS = ("thumb", "index", "middle", "ring", "pinky")    # the add-on's order (hr_hands_rig.h RIG_THUMB..RIG_PINKY)
TEX_SIZE = 1024

import skin_checker
from skin_checker import check as sc_check
POSES = skin_checker.POSES
FIST = POSES['FIST']


def curl_max(f, seg):
    """the angle a joint reaches at full curl (curl 1 in the add-on): Skin Checker's fist"""
    return float((FIST[1] if f == 'thumb' else FIST[0])[str(seg)])


def pose_degrees(key):
    fing, thumb, index = POSES[key]
    out = []
    for f in FINGERS:
        for s in (1, 2, 3):
            t = thumb if f == 'thumb' else (index if (f == 'index' and index) else fing)
            out.append(float(t.get(str(s), 0)))
    return out


report = {"side": SIDE, "mesh": MESH, "rig": RIG}
src = bpy.data.objects[MESH]
arm = bpy.data.objects[RIG]
props = bpy.context.scene.skin_checker
discs = props.discs
report["discs"] = discs.name if discs else None


# ---- the joint discs: a disc object whose matrix was applied (identity, mesh off-centre) gets a placed copy ----------
def placed_discs():
    """the joint planes Skin Checker's thin-joint measure needs. A file whose disc objects all sit in one spot (the left
    glove's 'cut discs' were saved with their places lost) gets planes made from the rig the way rig.build makes them:
    through each finger bone's head, square to the mean of the bone before it and this one."""
    if discs is not None:
        cs = np.array([np.array(o.matrix_world @ (sum((v.co for v in o.data.vertices), Vector()) / max(1, len(o.data.vertices))))
                       for o in discs.objects])
        if len(cs) >= 15 and np.ptp(cs, axis=0).max() > 0.01:
            return discs.name
    col = bpy.data.collections.new("joint planes from the rig")
    bpy.context.scene.collection.children.link(col)
    mw = arm.matrix_world
    for f in FINGERS:
        for i in (1, 2, 3):
            b = arm.data.bones[f'{f}_{i}']
            d_out = (mw @ b.tail_local - mw @ b.head_local).normalized()
            prev = b.parent
            d_in = (mw @ prev.tail_local - mw @ prev.head_local).normalized() if prev and prev.name != 'hand' else d_out
            n = (d_in + d_out).normalized()
            e = bpy.data.objects.new(f"plane {f} {i}", None)
            e.matrix_world = Matrix.Translation(mw @ b.head_local) @ n.to_track_quat('Z', 'Y').to_matrix().to_4x4()
            col.objects.link(e)
    report["discs_from_rig"] = True
    return col.name


DISCS = placed_discs()


def measure(ob, tag):
    out = {}
    for key in ('GRIP', 'TRIGGER', 'FIST'):
        skin_checker.apply_pose(arm, key)
        r = sc_check.skin_check(ob.name, False, discs=DISCS)
        out[key] = {"stretch_edges": r['stretch_edges'], "stretch_worst": r['squash_or_stretch_worst'],
                    "clip_pairs": r['clip_pairs'], "torn": r['tear_edges'], "thinnest_joint": r['thin_worst'],
                    "thin_joints": r['thin_joints']}
        print(f"CHECK {tag} {key}: stretched {r['stretch_edges']} {r['squash_or_stretch_worst']} clip {r['clip_pairs']} "
              f"torn {r['tear_edges']} thinnest {r['thin_worst']} thin {r['thin_joints']}", flush=True)
    skin_checker.apply_pose(arm, 'GRIP')
    return out


def activate(ob):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)


TEAR_JUMP = sc_check.TEAR_JUMP
MAX_SPLIT_ROUNDS = 6


def weights_from_full(ob):
    """every point's weights copied again from the full glove (nearest face, interpolated), then at most 4 bones a
    point, cleaned and normalised: what the game file holds"""
    activate(ob)
    # the full glove STRAIGHT: the transfer reads the source as evaluated, and the file keeps it bent into the grip
    # (the first try took every weight from the bent glove, 2026-11-27: thousands of tears)
    bends = [m for m in src.modifiers if m.type == 'ARMATURE']
    keep = [m.show_viewport for m in bends]
    for m in bends:
        m.show_viewport = False
    t = ob.modifiers.new("weights", 'DATA_TRANSFER'); t.object = src; t.use_vert_data = True
    t.data_types_verts = {'VGROUP_WEIGHTS'}; t.vert_mapping = 'POLYINTERP_NEAREST'
    t.layers_vgroup_select_src = 'ALL'; t.layers_vgroup_select_dst = 'NAME'
    bpy.ops.object.modifier_apply(modifier=t.name)
    for m, k in zip(bends, keep):
        m.show_viewport = k
    # the weight ops below touch only the selected points while a paint mask is on (the left glove's mesh had one:
    # 2026-11-27, points with up to 9 bones got through and the game's bend disagreed with Blender's): all of them
    me = ob.data
    me.use_paint_mask_vertex = False; me.use_paint_mask = False
    me.vertices.foreach_set('select', [True] * len(me.vertices))
    # Blender's own Limit Total still skipped points on the left glove with the masks off (cause not found,
    # 2026-11-27), so the cap is done here, point by point: the 4 heaviest bones kept (any under 0.0005 dropped),
    # the rest removed, the kept ones scaled to sum to 1
    vgs = {g.index: g for g in ob.vertex_groups}
    for v in me.vertices:
        ws = sorted(((g.weight, g.group) for g in v.groups), reverse=True)
        keep = [(w, gi) for w, gi in ws[:4] if w >= 0.0005] or ws[:1]
        drop = [gi for _, gi in ws if gi not in {k for _, k in keep}]
        for gi in drop:
            vgs[gi].remove([v.index])
        s = sum(w for w, _ in keep) or 1.0
        for w, gi in keep:
            vgs[gi].add([v.index], w / s, 'REPLACE')


def torn_edges(ob):
    me = ob.data; ng = len(ob.vertex_groups)
    Wt = np.zeros((len(me.vertices), ng))
    for v in me.vertices:
        for g in v.groups:
            Wt[v.index, g.group] = g.weight
    ed = np.empty(len(me.edges) * 2, int); me.edges.foreach_get('vertices', ed); ed = ed.reshape(-1, 2)
    return np.where(np.abs(Wt[ed[:, 0]] - Wt[ed[:, 1]]).max(axis=1) > TEAR_JUMP)[0]


def slim(faces):
    import bmesh
    ob = src.copy(); ob.data = src.data.copy(); ob.name = f"{L} glove game {faces}"
    bpy.context.scene.collection.objects.link(ob)
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    activate(ob)
    d = ob.modifiers.new("slim", 'DECIMATE'); d.decimate_type = 'COLLAPSE'
    d.ratio = faces / len(ob.data.polygons); d.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=d.name)
    after_decimate = len(ob.data.polygons)
    weights_from_full(ob)
    rounds = []
    # a slimmed triangle can lie across a whole joint, its two ends on different bones: that edge tears when bent.
    # Cut each such edge in two and copy the weights again, until none is left
    for _ in range(MAX_SPLIT_ROUNDS):
        bad = torn_edges(ob)
        rounds.append(int(len(bad)))
        if not len(bad):
            break
        bm = bmesh.new(); bm.from_mesh(ob.data); bm.edges.ensure_lookup_table()
        res = bmesh.ops.subdivide_edges(bm, edges=[bm.edges[i] for i in bad], cuts=1, use_grid_fill=False)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        bm.to_mesh(ob.data); bm.free(); ob.data.update()
        weights_from_full(ob)
    a = ob.modifiers.new("bend", 'ARMATURE'); a.object = arm; a.use_deform_preserve_volume = True
    report.setdefault("split", {})[str(faces)] = {"after_decimate": after_decimate, "torn_per_round": rounds,
                                                  "final_faces": len(ob.data.polygons)}
    print("SPLIT", faces, after_decimate, rounds, len(ob.data.polygons), flush=True)
    return ob


# ---- the grip frame ------------------------------------------------------------------------------------------------
def grip_frame():
    """OpenXR's grip pose, found on the glove in Skin Checker's grip pose: origin on the axis of the tube the four
    fingers wrap round (each finger's posed joints fitted with a circle across that axis, the centres averaged); -Z
    along the tube from the little finger to the index (spec: 'little finger to thumb'); +X the palm's normal, away
    from the palm on the left hand, into the palm on the right (spec); +Y = Z x X. The glove's palm faces -Y in the
    .blend (back +Y), so +X is -Y (left) / +Y (right) there, made square to Z. Returns (R columns = grip axes in .blend
    coordinates, centre, mean radius, details)."""
    skin_checker.apply_pose(arm, 'GRIP')
    mw = arm.matrix_world; pb = arm.pose.bones
    pts = {f: [mw @ pb[f'{f}_{i}'].head for i in (1, 2, 3)] + [mw @ pb[f'{f}_3'].tail] for f in FINGERS[1:]}
    a = (mw @ pb['index_1'].head) - (mw @ pb['pinky_1'].head); a.normalize()
    a = np.array(a)
    cens, radii = [], []
    for f in FINGERS[1:]:
        P = np.array([np.array(p) for p in pts[f]])
        # a 2D basis across the tube
        u = np.cross(a, [0, 0, 1.0]); u /= np.linalg.norm(u); v = np.cross(a, u)
        x, y = P @ u, P @ v
        A = np.c_[2 * x, 2 * y, np.ones(len(x))]; b = x * x + y * y
        (cx, cy, k), *_ = np.linalg.lstsq(A, b, rcond=None)
        r = math.sqrt(max(k + cx * cx + cy * cy, 0))
        along = float((P @ a).mean())
        cens.append(cx * u + cy * v + along * a); radii.append(r)
    C = np.array(cens)
    centre = C.mean(axis=0)
    # the tube axis through the four centres (oriented little finger -> index)
    _, _, vt = np.linalg.svd(C - centre); ax = vt[0]
    if ax @ a < 0:
        ax = -ax
    off_axis_deg = math.degrees(math.acos(min(1.0, abs(float(ax @ a)))))
    # the room inside the fist: the glove's own surface, bent into the grip, in the slab between the index and the
    # little finger, seen down the tube; the clearance of a spot = its distance to the nearest surface point there.
    # The circle centres' clearance is measured, and the spot with the most room within CLEAR_SEARCH_M of it found
    co = sc_check._coords(src, True)
    along = co @ ax
    lo, hi = float(min(np.array(mw @ pb['pinky_1'].head) @ ax, np.array(mw @ pb['index_1'].head) @ ax)), \
        float(max(np.array(mw @ pb['pinky_1'].head) @ ax, np.array(mw @ pb['index_1'].head) @ ax))
    slab = co[(along > lo + 0.005) & (along < hi - 0.005)]
    u = np.cross(ax, [0, 0, 1.0]); u /= np.linalg.norm(u); v = np.cross(ax, u)
    S2 = np.c_[slab @ u, slab @ v]
    c2 = np.array([centre @ u, centre @ v])
    def clearance(p2):
        return float(np.sqrt(((S2 - p2) ** 2).sum(axis=1)).min())
    best, best_c = c2, clearance(c2)
    for step in (0.002, 0.0005):
        span = CLEAR_SEARCH_M if step == 0.002 else 0.002
        g0 = best
        for dx in np.arange(-span, span + 1e-9, step):
            for dy in np.arange(-span, span + 1e-9, step):
                p2 = g0 + np.array([dx, dy])
                if np.linalg.norm(p2 - c2) > CLEAR_SEARCH_M:
                    continue
                c_ = clearance(p2)
                if c_ > best_c:
                    best, best_c = p2, c_
    circle_clear = clearance(c2)
    roomiest = best[0] * u + best[1] * v + float(centre @ ax) * ax
    if CENTRE == 'room':
        centre = roomiest
    Z = -ax
    xb = np.array([0, 1.0, 0]) if SIDE == 'right' else np.array([0, -1.0, 0])
    X = xb - (xb @ Z) * Z; X /= np.linalg.norm(X)
    Y = np.cross(Z, X)
    R = np.c_[X, Y, Z]
    return R, centre, float(np.mean(radii)), {"centre_used": CENTRE,
                                               "clearance_at_circle_centre_m": round(circle_clear, 4),
                                               "roomiest_spot_blend": [round(float(x), 4) for x in roomiest],
                                               "clearance_at_roomiest_m": round(best_c, 4),
                                               "roomiest_from_circle_centre_m": round(float(np.linalg.norm(best - c2)), 4),
                                               "finger_circle_radius_m": [round(r, 4) for r in radii],
                                               "tube_axis_vs_knuckle_line_deg": round(off_axis_deg, 1),
                                               "centres": [[round(float(c), 4) for c in cc] for cc in C]}


# ---- export ----------------------------------------------------------------------------------------------------------
def base_colour_image(ob):
    for m in ob.data.materials:
        if not m or not m.node_tree:
            continue
        bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is None:
            continue
        inp = bsdf.inputs[0]                      # Base Color is always the first input
        stack = [l.from_node for l in inp.links]
        while stack:
            n = stack.pop()
            if n.type == 'TEX_IMAGE' and n.image:
                return n.image
            for i in n.inputs:
                stack += [l.from_node for l in i.links]
    return None


def write_tga(img, path):
    im = img.copy(); im.scale(TEX_SIZE, TEX_SIZE)
    px = np.empty(TEX_SIZE * TEX_SIZE * 4, np.float32); im.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    # Blender keeps colour images' pixels as stored (sRGB bytes / 255 for 8-bit files)
    bgr = (np.clip(px[:, [2, 1, 0]], 0, 1) * 255 + 0.5).astype(np.uint8)
    with open(path, "wb") as f:
        f.write(struct.pack("<BBBHHBHHHHBB", 0, 0, 2, 0, 0, 0, 0, 0, TEX_SIZE, TEX_SIZE, 24, 0))
        f.write(bgr.tobytes())
    bpy.data.images.remove(im)


def export(ob, R, centre, radius):
    me = ob.data
    Rt = Matrix([list(R[:, 0]), list(R[:, 1]), list(R[:, 2])])          # rows = grip axes: .blend -> grip
    c = Vector(centre)
    def to_grip_p(p): return Rt @ (Vector(p) - c)
    def to_grip_n(n): return (Rt @ Vector(n)).normalized()
    bones = [arm.data.bones['hand']] + [arm.data.bones[f'{f}_{i}'] for f in FINGERS for i in (1, 2, 3)]
    bidx = {b.name: i for i, b in enumerate(bones)}
    gname = {g.index: g.name for g in ob.vertex_groups}
    me.calc_loop_triangles()
    uv = me.uv_layers.active.data
    cn = me.corner_normals
    W = ob.matrix_world
    key_of, verts, src_of, idx = {}, [], [], []
    for t in me.loop_triangles:
        for li, vi in zip(t.loops, t.vertices):
            u = uv[li].uv; n = cn[li].vector
            k = (vi, round(u.x, 5), round(u.y, 5), round(n.x, 3), round(n.y, 3), round(n.z, 3))
            j = key_of.get(k)
            if j is None:
                j = key_of[k] = len(verts)
                v = me.vertices[vi]
                # kept in Blender's own order: the blend lines each bone's sign up with the sum so far, so the order
                # decides the rare point shared by bones turned far apart (a tight fist), and this one is Blender's
                gs = [(g.weight, bidx[gname[g.group]]) for g in v.groups if g.weight > 0 and gname[g.group] in bidx]
                if len(gs) > 4:
                    raise ValueError(f"point {vi} follows {len(gs)} bones after the cap of 4")
                s = sum(w for w, _ in gs) or 1.0
                gs = [(w / s, b) for w, b in gs] + [(0.0, 0)] * (4 - len(gs))
                verts.append((to_grip_p(W @ v.co), to_grip_n(W.to_3x3() @ n), (u.x, u.y), gs))
                src_of.append(vi)
            idx.append(j)
    path = os.path.join(OUT, f"hand_{SIDE}.hrsk")
    with open(path, "wb") as f:
        f.write(b"HRSK"); f.write(struct.pack("<5I", 1, len(bones), len(verts), len(idx), 1 if SIDE == 'right' else 0))
        f.write(struct.pack("<4f", *centre, radius))
        A = Matrix(arm.matrix_world)
        G = Rt.to_4x4() @ Matrix.Translation(-c)
        for b in bones:
            M = G @ A @ b.matrix_local
            nm = b.name.encode()[:15].ljust(16, b"\0")
            par = bidx[b.parent.name] if b.parent else -1
            f.write(nm); f.write(struct.pack("<i", par))
            f.write(struct.pack("<12f", *[M[r][cc] for r in range(3) for cc in range(4)]))
            f.write(struct.pack("<f", 0.0 if b.name == 'hand' else curl_max(*b.name.rsplit('_', 1)[0:1], int(b.name[-1]))))
        for p, n, (uu, vv), gs in verts:
            f.write(struct.pack("<8f", p.x, p.y, p.z, n.x, n.y, n.z, uu, vv))
            f.write(struct.pack("<4B", *[b for _, b in gs])); f.write(struct.pack("<4f", *[w for w, _ in gs]))
        f.write(np.array(idx, np.uint32).tobytes())
    # golden: Blender's own bend, per game point
    gpath = os.path.join(OUT, f"hand_{SIDE}_golden.bin")
    with open(gpath, "wb") as f:
        f.write(b"HRSG"); f.write(struct.pack("<2I", len(verts), 2))
        for key in ('GRIP', 'FIST'):
            skin_checker.apply_pose(arm, key)
            co = sc_check._coords(ob, True)
            f.write(struct.pack("<15f", *pose_degrees(key)))
            f.write(np.array([list(to_grip_p(co[vi])) for vi in src_of], np.float32).tobytes())
    skin_checker.apply_pose(arm, 'GRIP')
    img = base_colour_image(ob)
    if img:
        write_tga(img, os.path.join(OUT, f"hand_{SIDE}.tga"))
    return {"file": os.path.basename(path), "points": len(verts), "triangles": len(idx) // 3, "blender_vertices": len(me.vertices),
            "bytes": os.path.getsize(path), "texture": img.name if img else None}


report["full"] = {"faces": len(src.data.polygons), "vertices": len(src.data.vertices), "check": measure(src, "full")}
R, centre, radius, gd = grip_frame()
report["grip"] = {"centre_blend": [round(float(x), 4) for x in centre], "tube_radius_m": round(radius, 4),
                  "axes_blend_XYZ": [[round(float(x), 4) for x in R[:, i]] for i in range(3)], **gd}
print("GRIP", json.dumps(report["grip"]), flush=True)
report["slim"] = {}
last = None
for n in FACES:
    ob = slim(n)
    report["slim"][str(n)] = {"faces": len(ob.data.polygons), "vertices": len(ob.data.vertices), "check": measure(ob, f"slim {n}")}
    last = ob
report["export"] = export(last, R, centre, radius)
print("EXPORT", json.dumps(report["export"]), flush=True)
with open(os.path.join(OUT, f"hand_{SIDE}_report.json"), "w") as f:
    json.dump(report, f, indent=1)
# the slimmed glove for Tefa's eye, in its own file (the source .blend is left as it was)
for o in list(bpy.data.objects):
    if o.name.startswith(f"{L} glove game") and o is not last:
        bpy.data.objects.remove(o)
src.hide_set(True); last.hide_set(False)
gb = os.path.join(os.path.dirname(bpy.data.filepath), f"meshy_hand_{SIDE}_game.blend")
bpy.ops.wm.save_as_mainfile(filepath=gb, copy=True)
print("SAVED", gb, flush=True)
