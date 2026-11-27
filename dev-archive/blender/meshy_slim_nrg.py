"""Slim the fitted Meshy gun and write it in the game camera's frame of the cln1 rip, with its UVs; save its three
textures; render the slim one beside the full one.
blender -b <fitted.blend> -P meshy_slim.py -- <rips> <base_groups.json> <faces> <out folder>"""
import bpy, sys, os, json
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
rips, groups_json, faces, out = argv[0], argv[1], int(argv[2]), argv[3]
os.makedirs(out, exist_ok=True)

# where the base frame was centred from: its box centre in the rip's Blender coordinates
before = set(bpy.data.objects)
bpy.ops.wm.obj_import(filepath=os.path.join(rips, "nrg1", "gun.obj"), forward_axis="NEGATIVE_Z", up_axis="Y")
rip = [o for o in bpy.data.objects if o not in before]
base_names = set(json.load(open(groups_json))["nrg"]["base"])
vs = [o.matrix_world @ v.co for o in rip if o.name in base_names for v in o.data.vertices]
lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
c = (lo + hi) / 2
for o in rip:
    bpy.data.objects.remove(o)
print("base frame centre (Blender coords of the rip):", tuple(round(x, 4) for x in c))

for o in list(bpy.data.objects):
    if o.type == "MESH" and o.name.startswith("meshy") and len(o.data.vertices) < 100:
        bpy.data.objects.remove(o)           # Meshy's stray cube
m = next(o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("meshy"))
full_faces = len(m.data.polygons)
slim = m.copy(); slim.data = m.data.copy(); slim.name = "meshy_slim"
bpy.context.scene.collection.objects.link(slim)
mod = slim.modifiers.new("dec", "DECIMATE")
mod.ratio = faces / full_faces
bpy.context.view_layer.objects.active = slim
bpy.ops.object.modifier_apply(modifier="dec")
# into the rip's frame: + c (Blender coords), then Blender (X, Y, Z) -> game (x, y, z) = (X, Z, -Y)
slim.matrix_world = Matrix.Translation(c) @ slim.matrix_world
print("slim: %d -> %d faces, %d vertices" % (full_faces, len(slim.data.polygons), len(slim.data.vertices)))

# write the OBJ by hand: v in the game camera frame, vt as Blender has them, triangles
me = slim.data
me.calc_loop_triangles()
uv = me.uv_layers.active.data
W = slim.matrix_world
path = os.path.join(out, "meshy_nrg_slim.obj")
with open(path, "w", newline="\n") as f:
    f.write("# Meshy gun, slimmed; game camera frame of the cln1 rip (x right, y up, -z ahead), metres; vt as Blender\n")
    for v in me.vertices:
        p = W @ v.co
        f.write("v %.6f %.6f %.6f\n" % (p.x, p.z, -p.y))
    vt_index = {}
    lines = []
    for t in me.loop_triangles:
        cs = []
        for li, vi in zip(t.loops, t.vertices):
            key = (round(uv[li].uv.x, 6), round(uv[li].uv.y, 6))
            if key not in vt_index:
                vt_index[key] = len(vt_index) + 1
                f.write("vt %.6f %.6f\n" % key)
            cs.append("%d/%d" % (vi + 1, vt_index[key]))
        lines.append("f " + " ".join(cs) + "\n")
    f.writelines(lines)
print("WROTE", path, len(me.loop_triangles), "triangles")

# the three textures
mat = m.data.materials[0]
for n in mat.node_tree.nodes:
    if n.type == "TEX_IMAGE":
        role = n.outputs[0].links[0].to_node.type if n.outputs[0].links else "?"
        name = {"BSDF_PRINCIPLED": "colour", "SEPRGB": "orm", "SEPARATE_COLOR": "orm", "NORMAL_MAP": "normal"}.get(role, role)
        img = n.image
        img.filepath_raw = os.path.join(out, "meshy_nrg_%s.png" % name)
        img.file_format = "PNG"
        img.save()
        print("TEX", name, img.size[:])

# picture: full (left) and slim (right), same view
slim.matrix_world = Matrix.Translation(-c) @ slim.matrix_world
off = Vector((0.45, 0, 0))
slim.location += off
for o in bpy.data.objects:
    if o.type == "MESH" and o not in (m, slim):
        o.hide_render = True
sc = bpy.context.scene
pts = [o.matrix_world @ Vector(k) for o in (m, slim) for k in o.bound_box]
cen = sum(pts, Vector()) / len(pts)
size = max(max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3))
cam = sc.camera
if cam is None:
    cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.type = "ORTHO"
    try:
        sc.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 1400, 700
    sc.world = bpy.data.worlds.new("w")
    for loc, e in (((1, -0.5, 1.2), 300), ((-1, 0.5, 0.6), 150), ((1, 0.5, -0.4), 100)):
        d = bpy.data.lights.new("l", "AREA"); d.energy = e * size * size; d.size = size * 2
        lo_ = bpy.data.objects.new("l", d); sc.collection.objects.link(lo_)
        lo_.location = cen + Vector(loc) * size * 2
        lo_.rotation_euler = (cen - lo_.location).to_track_quat("-Z", "Y").to_euler()
cam.data.ortho_scale = size * 1.05
for name, dv in (("side", Vector((1, 0, 0.05))), ("close", Vector((1, -0.4, 0.3)))):
    if name == "close":
        cam.data.ortho_scale = size * 0.45
        cen2 = Vector((m.matrix_world.translation.x, cen.y + 0.12, cen.z))
        tgt = cen2
    else:
        tgt = cen
    cam.location = tgt + dv.normalized() * size * 3
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, "picture_full_vs_slim_%s.png" % name)
    bpy.ops.render.render(write_still=True)
