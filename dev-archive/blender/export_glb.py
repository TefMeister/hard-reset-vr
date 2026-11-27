"""Each morph's ripped gun (textured, HUD dial and crosshair left out, parts joined) + its fitted handle -> one GLB.
blender -b --factory-startup -P export_glb.py -- <rips folder> <game folder with d3d9_vr.ini> <out folder>"""
import bpy, sys, os, re
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
rips, game, out = argv
fit = os.path.join(rips, "fit")
os.makedirs(out, exist_ok=True)
NAMES = {"cln1": "rifle", "cln2": "shotgun", "cln3": "grenade", "cln4": "rocket", "cln5": "mine",
         "nrg1": "plasma", "nrg2": "shock", "nrg3": "mortar", "nrg4": "railgun", "nrg5": "smartgun"}
grips, sec = {}, None
for l in open(os.path.join(game, "d3d9_vr.ini"), encoding="latin1"):
    m = re.match(r"\[pose\.(\w+)\]", l.strip())
    if l.strip().startswith("["):
        sec = m.group(1) if m else None
    elif sec and l.startswith("gun_grip"):
        grips[sec] = [float(t) for t in l.split("=")[1].split()]


def imp(path):
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=path, forward_axis="NEGATIVE_Z", up_axis="Y")
    return [o for o in bpy.data.objects if o not in before]


for m, nice in NAMES.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    gun = []
    for o in imp(os.path.join(rips, m, "gun.obj")):
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        if max(p.x for p in pts) < 0 or min(p.y for p in pts) < 0.1:
            bpy.data.objects.remove(o)
        else:
            gun.append(o)
    bpy.ops.object.select_all(action="DESELECT")
    for o in gun:
        o.select_set(True)
    bpy.context.view_layer.objects.active = gun[0]
    bpy.ops.object.join()
    g = bpy.context.view_layer.objects.active
    g.name = "gun_" + nice
    h = imp(os.path.join(fit, "gun_handle_%s.obj" % m))[0]
    h.name = "handle"
    x, y, z = grips[m]
    h.location = Vector((x, -z, y))
    mat = bpy.data.materials.new("handle"); mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs[0].default_value = (0.25, 0.25, 0.26, 1)
    h.data.materials.clear(); h.data.materials.append(mat)
    # centre the pair on the origin
    allp = [o.matrix_world @ Vector(c) for o in (g, h) for c in o.bound_box]
    c = sum(allp, Vector()) / len(allp)
    for o in (g, h):
        o.location -= c
    path = os.path.join(out, "hard_reset_%s_%s_with_handle.glb" % (m, nice))
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB")
    print("WROTE", path, os.path.getsize(path) // 1024, "KB", len(g.data.polygons) + len(h.data.polygons), "faces")
