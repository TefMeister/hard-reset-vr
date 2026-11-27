"""Skin Checker, the check: measure a skinned (armature-bent) mesh for the faults the eye finds.
Used by the add-on's "Check bend" button; from a script: from skin_checker.check import skin_check.

What it measures, posed against rest (the mesh with the armature off):
  stretch : edges longer than STRETCH_MAX x or shorter than SQUASH_MIN x their rest length
  clip    : face pairs that pass through each other when posed but did NOT in rest (Meshy shells already
            overlap themselves in places; only NEW crossings count), faces sharing a vertex ignored
  tear    : edges whose two ends are pulled by different bones (largest weight difference > TEAR_JUMP),
            which is what leaves flaps and spikes standing off the surface
  thin    : per joint, the ring of skin round it: its width across the finger bent against straight; below
            THIN_MIN the finger goes thin at that bend (Tefa's eye found it 2026-11-27 after the other three
            were clean). Needs the joint discs collection.
Each fault is put in a "spot" (a 12 mm grid cell); the spots are returned worst first, with the bones involved,
so pictures can be taken there. It also builds an object "<name> faults" that marks the faulty faces in red,
for the close-ups (delete it after)."""
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

STRETCH_MAX = 1.6
SQUASH_MIN = 0.5
TEAR_JUMP = 0.5
THIN_MIN = 0.92     # a joint whose bent width is below this share of its straight width counts as thinned
RING = 0.002        # the ring of skin measured at each joint: this far either side of the joint's plane
CELL = 0.012
MIN_EDGE = 0.0003


def _coords(ob, posed):
    arm = [m for m in ob.modifiers if m.type == 'ARMATURE']
    keep = [m.show_viewport for m in arm]
    for m in arm:
        m.show_viewport = posed
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    ev = ob.evaluated_get(dg); me = ev.to_mesh()
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co)
    ev.to_mesh_clear()
    for m, k in zip(arm, keep):
        m.show_viewport = k
    return co.reshape(-1, 3)


def _overlaps(co, polys):
    bvh = BVHTree.FromPolygons([tuple(v) for v in co], polys, all_triangles=False, epsilon=0.0)
    out = set()
    for a, b in bvh.overlap(bvh):
        if a < b and not (set(polys[a]) & set(polys[b])):
            out.add((a, b))
    return out


def skin_check(name, mark=True, stretch_max=STRETCH_MAX, squash_min=SQUASH_MIN, tear_jump=TEAR_JUMP, discs=None):
    ob = bpy.data.objects[name]; me = ob.data
    rest = _coords(ob, False); pose = _coords(ob, True)
    nv = len(me.vertices)
    groups = [g.name for g in ob.vertex_groups]
    W = np.zeros((nv, len(groups)))
    for v in me.vertices:
        for g in v.groups:
            W[v.index, g.group] = g.weight
    dom = W.argmax(axis=1)
    ed = np.empty(len(me.edges) * 2, int); me.edges.foreach_get('vertices', ed); ed = ed.reshape(-1, 2)
    rl = np.linalg.norm(rest[ed[:, 0]] - rest[ed[:, 1]], axis=1)
    pl = np.linalg.norm(pose[ed[:, 0]] - pose[ed[:, 1]], axis=1)
    ok = rl > MIN_EDGE
    ratio = np.where(ok, pl / np.maximum(rl, 1e-9), 1.0)
    stretch = np.where(ok & ((ratio > stretch_max) | (ratio < squash_min)))[0]
    jump = np.abs(W[ed[:, 0]] - W[ed[:, 1]]).max(axis=1)
    tear = np.where(jump > tear_jump)[0]
    # thinning, per joint: the ring of skin round each joint (within RING of its plane, owned by that finger),
    # its mean width across the finger, straight against bent (across = perpendicular to the average of the two
    # bones' directions)
    arm_ob = next((m.object for m in ob.modifiers if m.type == 'ARMATURE' and m.object), None)
    thin = np.array([], int); joints = {}
    if arm_ob is not None and discs:
        mw = arm_ob.matrix_world
        pb = arm_ob.pose.bones
        def bdir(name, posed):
            b = pb[name]
            h, t = (b.head, b.tail) if posed else (b.bone.head_local, b.bone.tail_local)
            v = (mw @ t) - (mw @ h); return np.array(v.normalized())
        planes = {o.name.split(' ', 1)[1]: (np.array(o.matrix_world.translation), np.array((o.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()))
                  for o in bpy.data.collections[discs].objects}
        # each point's finger: the one whose bone line is nearest at rest
        fingers = sorted({k.split(' ')[0] for k in planes})
        def line(f):
            pts = [np.array(mw @ pb[f'{f}_{i}'].bone.head_local) for i in (1, 2, 3)] + [np.array(mw @ pb[f'{f}_3'].bone.tail_local)]
            d = np.full(nv, 9.0)
            for a, b in zip(pts[:-1], pts[1:]):
                ab = b - a; t = np.clip(((rest - a) @ ab) / (ab @ ab), 0, 1); d = np.minimum(d, np.linalg.norm(rest - (a + t[:, None] * ab), axis=1))
            return d
        D = np.stack([line(f) for f in fingers]); own = D.argmin(axis=0); dmin = D.min(axis=0)
        bad = []
        for k, (o, nr) in planes.items():
            f, i = k.split(' '); i = int(i); fi = fingers.index(f)
            ring = np.where((own == fi) & (dmin < 0.02) & (np.abs((rest - o) @ nr) < RING))[0]
            if len(ring) < 8:
                continue
            prev = 'hand' if i == 1 else f'{f}_{i - 1}'
            def width(co, ax):
                ax = ax / np.linalg.norm(ax); q = co - np.outer(co @ ax, ax); c = q.mean(axis=0)
                return float(np.linalg.norm(q - c, axis=1).mean())
            w0 = width(rest[ring], bdir(prev, False) + bdir(f'{f}_{i}', False))
            w1 = width(pose[ring], bdir(prev, True) + bdir(f'{f}_{i}', True))
            joints[k] = round(w1 / w0, 2)
            if w1 / w0 < THIN_MIN:
                bad.extend(ring.tolist())
        thin = np.array(bad, int)
    thin_worst = min(joints.values()) if joints else 1.0
    polys = [tuple(p.vertices) for p in me.polygons]
    clip = _overlaps(pose, polys) - _overlaps(rest, polys)
    # spots
    spots = {}
    def add(kind, verts):
        c = rest[list(verts)].mean(axis=0)
        key = tuple((c // CELL).astype(int))
        s = spots.setdefault(key, {'stretch': 0, 'clip': 0, 'tear': 0, 'thin': 0, 'bones': set(), 'pts': []})
        s[kind] += 1; s['pts'].append(pose[list(verts)].mean(axis=0))
        for v in verts:
            s['bones'].add(groups[dom[v]])
    for e in stretch:
        add('stretch', ed[e])
    for e in tear:
        add('tear', ed[e])
    for a, b in clip:
        add('clip', polys[a] + polys[b])
    for v in thin:
        add('thin', (int(v),))
    ranked = sorted(spots.values(), key=lambda s: -(s['stretch'] + 3 * s['clip'] + s['tear'] + s['thin']))
    for s in ranked:
        s['centre'] = tuple(np.round(np.mean(s['pts'], axis=0), 4)); del s['pts']
        s['bones'] = sorted(s['bones'])
    if mark:
        bad = set()
        for e in list(stretch) + list(tear):
            bad.update(ed[e].tolist())
        bad.update(int(v) for v in thin)
        badf = {i for i, p in enumerate(polys) if set(p) & bad}
        for a, b in clip:
            badf.update((a, b))
        old = bpy.data.objects.get(name + ' faults')
        if old:
            bpy.data.objects.remove(old)
        bm = bmesh.new(); vmap = {}
        for fi in badf:
            vs = []
            for v in polys[fi]:
                if v not in vmap:
                    vmap[v] = bm.verts.new(Vector(pose[v]))
                vs.append(vmap[v])
            try:
                bm.faces.new(vs)
            except ValueError:
                pass
        m2 = bpy.data.meshes.new(name + ' faults'); bm.to_mesh(m2); bm.free()
        mat = bpy.data.materials.get('fault_red') or bpy.data.materials.new('fault_red')
        mat.use_nodes = True
        b = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        b.inputs['Base Color'].default_value = (1, 0, 0, 1)
        for nm in ('Emission Color', 'Emission'):
            if nm in b.inputs:
                b.inputs[nm].default_value = (1, 0, 0, 1); break
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value = 1.5
        mat.diffuse_color = (1, 0, 0, 1)
        m2.materials.append(mat)
        fo = bpy.data.objects.new(name + ' faults', m2); bpy.context.scene.collection.objects.link(fo)
        fo.show_in_front = True; fo.hide_render = False
    return {'stretch_edges': int(len(stretch)), 'squash_or_stretch_worst': (round(float(ratio[ok].min()), 2), round(float(ratio[ok].max()), 2)),
            'clip_pairs': len(clip), 'tear_edges': int(len(tear)),
            'thin_joints': {k: v for k, v in sorted(joints.items()) if v < THIN_MIN}, 'thin_worst': round(thin_worst, 2),
            'joint_width': dict(sorted(joints.items())), 'thin_points': int(len(thin)), 'spots': ranked}
