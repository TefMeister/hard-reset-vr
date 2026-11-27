"""Skin Checker, the check: measure a skinned (armature-bent) mesh for the faults the eye finds.
Used by the add-on's "Check bend" button; from a script: from skin_checker.check import skin_check.

What it measures, posed against rest (the mesh with the armature off):
  stretch : edges longer than STRETCH_MAX x or shorter than SQUASH_MIN x their rest length
  clip    : face pairs that pass through each other when posed but did NOT in rest (Meshy shells already
            overlap themselves in places; only NEW crossings count), faces sharing a vertex ignored
  tear    : edges whose two ends are pulled by different bones (largest weight difference > TEAR_JUMP),
            which is what leaves flaps and spikes standing off the surface
Each fault is put in a "spot" (a 12 mm grid cell); the spots are returned worst first, with the bones involved,
so pictures can be taken there. It also builds an object "<name> faults" that marks the faulty faces in red,
for the close-ups (delete it after)."""
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

STRETCH_MAX = 1.6
SQUASH_MIN = 0.5
TEAR_JUMP = 0.5
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


def skin_check(name, mark=True, stretch_max=STRETCH_MAX, squash_min=SQUASH_MIN, tear_jump=TEAR_JUMP):
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
    polys = [tuple(p.vertices) for p in me.polygons]
    clip = _overlaps(pose, polys) - _overlaps(rest, polys)
    # spots
    spots = {}
    def add(kind, verts):
        c = rest[list(verts)].mean(axis=0)
        key = tuple((c // CELL).astype(int))
        s = spots.setdefault(key, {'stretch': 0, 'clip': 0, 'tear': 0, 'bones': set(), 'pts': []})
        s[kind] += 1; s['pts'].append(pose[list(verts)].mean(axis=0))
        for v in verts:
            s['bones'].add(groups[dom[v]])
    for e in stretch:
        add('stretch', ed[e])
    for e in tear:
        add('tear', ed[e])
    for a, b in clip:
        add('clip', polys[a] + polys[b])
    ranked = sorted(spots.values(), key=lambda s: -(s['stretch'] + 3 * s['clip'] + s['tear']))
    for s in ranked:
        s['centre'] = tuple(np.round(np.mean(s['pts'], axis=0), 4)); del s['pts']
        s['bones'] = sorted(s['bones'])
    if mark:
        bad = set()
        for e in list(stretch) + list(tear):
            bad.update(ed[e].tolist())
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
            'clip_pairs': len(clip), 'tear_edges': int(len(tear)), 'spots': ranked}
