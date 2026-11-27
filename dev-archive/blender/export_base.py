"""The base frame of each gun (parts that stay put in all five modes, in mode 1's pose) as GLB: one file with the
frame only, one with the frame and our fitted handle as a separate object. Also the moving parts (mode 1) on their own.
blender -b --factory-startup -P export_base.py -- <rips> <game folder> <base_groups.json> <out folder>"""
import bpy, sys, os, re, json
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
rips, game, groups_json, out = argv
G = json.load(open(groups_json))
os.makedirs(out, exist_ok=True)
NAMES = {"cln": ("cln1", "bullet_gun"), "nrg": ("nrg1", "energy_gun")}
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


def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    j = bpy.context.view_layer.objects.active
    j.name = name
    return j


def export(path, objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True)
    print("WROTE", os.path.basename(path), os.path.getsize(path) // 1024, "KB",
          sum(len(o.data.polygons) for o in objs), "faces")


for gun, (m, nice) in NAMES.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objs = imp(os.path.join(rips, m, "gun.obj"))
    base = [o for o in objs if o.name in G[gun]["base"]]
    moving = [o for o in objs if o.name in G[gun]["moving"]]
    for o in objs:
        if o not in base and o not in moving:
            bpy.data.objects.remove(o)
    b = join(base, "%s_base_frame" % nice)
    mv = join(moving, "%s_moving_parts_mode1" % nice)
    h = imp(os.path.join(rips, "fit", "gun_handle_%s.obj" % m))[0]
    h.name = "%s_handle" % nice
    x, y, z = grips[m]
    h.location = Vector((x, -z, y))
    mat = bpy.data.materials.new("handle"); mat.use_nodes = True
    next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs[0].default_value = (0.25, 0.25, 0.26, 1)
    h.data.materials.clear(); h.data.materials.append(mat)
    pts = [b.matrix_world @ Vector(c) for c in b.bound_box]
    c = sum(pts, Vector()) / len(pts)
    for o in (b, mv, h):
        o.location -= c          # the same shift for all three: they still fit together
    export(os.path.join(out, "hard_reset_%s_base_frame.glb" % nice), [b])
    export(os.path.join(out, "hard_reset_%s_base_frame_with_handle.glb" % nice), [b, h])
    export(os.path.join(out, "hard_reset_%s_moving_parts_mode1.glb" % nice), [mv])
    bpy.ops.object.select_all(action="DESELECT")
    for o in (b, h):
        o.select_set(True)
    mv.hide_render = True
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 1200, 700
    sc.world = bpy.data.worlds.new("w")
    bg = sc.world.node_tree.nodes["Background"] if sc.world.node_tree else None
    if bg:
        bg.inputs[0].default_value = (0.22, 0.22, 0.24, 1); bg.inputs[1].default_value = 1.5
    pts = [o.matrix_world @ Vector(cc) for o in (b, h) for cc in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    cen, size = (mn + mx) / 2, max(mx - mn)
    for loc, e in (((1, -0.5, 1.2), 300), ((-1, 0.5, 0.6), 150), ((1, 0.5, -0.4), 100)):
        d = bpy.data.lights.new("l", "AREA"); d.energy = e * size * size; d.size = size * 2
        lo = bpy.data.objects.new("l", d); sc.collection.objects.link(lo)
        lo.location = cen + Vector(loc) * size * 2
        lo.rotation_euler = (cen - lo.location).to_track_quat("-Z", "Y").to_euler()
    cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.type = "ORTHO"; cd.ortho_scale = size * 1.1
    for name, dv in (("side", Vector((1, 0, 0.1))), ("angle", Vector((1, -0.7, 0.5)))):
        cam.location = cen + dv.normalized() * size * 3
        cam.rotation_euler = (cen - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, "picture_%s_base_frame_with_handle_%s.png" % (nice, name))
        bpy.ops.render.render(write_still=True)
