"""Meshy's textured gun + Meshy's part-split copy of it -> the textured gun slimmed and cut into those parts, with its
own paint (2026-11-28). Run inside Blender (the live one, or blender -b -P own_guns_split.py -- <folder>).

Meshy's split file has no UVs and no textures, is about 15.86 times smaller and sits with its base at z 0; its parts
have the same shape as the textured model. So: the split parts are laid over the textured model by their bounding
boxes, the textured model is slimmed (its UVs kept), and every face of the slim model takes the part whose surface is
nearest; then the slim model is separated by that label. Measured: rifle median gap 2 mm, shotgun 5 mm on a 1.9-unit
model. Then each gun is written gun-local (right, ahead with 0 at the muzzle tip, up from the barrel line), metres,
with its three textures, for build_own_guns.py.
"""
import bpy, os, sys
import numpy as np
from mathutils import kdtree

FOLDER = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else r"D:\Hard Reset GLB"
OUT = os.path.join(FOLDER, "work")
FACES = 20000
EVERY = 4                # every 4th vertex of the split parts goes in the search tree
MESHY_LENGTH = 1.903     # Meshy's models come about this long
# name, a word of the file name, the length in metres it gets, the muzzle tip (x, y, z) in Meshy's units
GUNS = [("rifle", "futuristic", 0.80, (-0.953, 0.007, 0.186)), ("shotgun", "cyborg", 0.85, (-0.952, -0.001, 0.247))]


def world_points(o):
    n = len(o.data.vertices)
    a = np.empty(n * 3, "f"); o.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
    M = np.array(o.matrix_world)
    return a @ M[:3, :3].T + M[:3, 3]


def load(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before and o.type == "MESH"]


os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_homefile(use_empty=True)
files = sorted(os.listdir(FOLDER))
for name, word, length, muz in GUNS:
    tex = load(os.path.join(FOLDER, next(f for f in files if word in f and f.endswith("_texture.glb"))))[0]
    parts = sorted(load(os.path.join(FOLDER, next(f for f in files if word in f and "split" in f))), key=lambda o: o.name)
    P = [world_points(o) for o in parts]
    allp, tp = np.vstack(P), world_points(tex)
    slo, shi, tlo, thi = allp.min(0), allp.max(0), tp.min(0), tp.max(0)
    k = (thi - tlo) / (shi - slo)
    kd = kdtree.KDTree(sum(len(p[::EVERY]) for p in P))
    label = []
    for i, p in enumerate(P):
        for v in (p[::EVERY] - slo) * k + tlo:
            kd.insert(v, len(label)); label.append(i)
    kd.balance()
    for o in parts:
        bpy.data.objects.remove(o)
    col = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(col)
    for c in tex.users_collection:
        c.objects.unlink(tex)
    col.objects.link(tex); tex.name = name + "_part"
    bpy.ops.object.select_all(action="DESELECT"); tex.select_set(True); bpy.context.view_layer.objects.active = tex
    m = tex.modifiers.new("slim", "DECIMATE"); m.ratio = FACES / len(tex.data.polygons)
    bpy.ops.object.modifier_apply(modifier="slim")
    me = tex.data
    while len(me.materials) < len(P):
        me.materials.append(me.materials[0])
    gaps = []
    for f in me.polygons:
        _, i, gap = kd.find(tex.matrix_world @ f.center)
        f.material_index = label[i]; gaps.append(gap)
    print("%s: %d faces, gap to its part median %.4f, worst %.4f" % (name, len(me.polygons), np.median(gaps), max(gaps)))
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="MATERIAL"); bpy.ops.object.mode_set(mode="OBJECT")

    s = length / MESHY_LENGTH
    nv, vts, faces = 0, {}, []
    with open(os.path.join(OUT, name + "_local.obj"), "w", newline="\n") as f:
        f.write("# %s, gun-local metres: right, ahead (0 at the muzzle tip), up from the barrel line\n" % name)
        for o in sorted(col.objects, key=lambda o: o.name):
            me = o.data; me.calc_loop_triangles(); uv = me.uv_layers.active.data
            for v in me.vertices:
                f.write("v %.6f %.6f %.6f\n" % ((v.co.y - muz[1]) * s, -(v.co.x - muz[0]) * s, (v.co.z - muz[2]) * s))
            for t in me.loop_triangles:
                cs = []
                for li, vi in zip(t.loops, t.vertices):
                    key = (round(uv[li].uv.x, 6), round(uv[li].uv.y, 6))
                    if key not in vts:
                        vts[key] = len(vts) + 1; f.write("vt %.6f %.6f\n" % key)
                    cs.append("%d/%d" % (vi + 1 + nv, vts[key]))
                faces.append("f " + " ".join(cs) + "\n")
            nv += len(me.vertices)
        f.writelines(faces)
    for n in col.objects[0].data.materials[0].node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.outputs[0].links:
            role = {"BSDF_PRINCIPLED": "colour", "SEPRGB": "orm", "SEPARATE_COLOR": "orm",
                    "NORMAL_MAP": "normal"}.get(n.outputs[0].links[0].to_node.type)
            if role:
                n.image.filepath_raw = os.path.join(OUT, "%s_%s.png" % (name, role)); n.image.file_format = "PNG"; n.image.save()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "two-guns-split-textured.blend"))
