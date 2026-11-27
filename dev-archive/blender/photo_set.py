"""Photo set of a fitted Meshy gun as the game draws it: Meshy slimmed to N faces + the game's moving parts.
blender -b <fitted.blend> -P photo_set.py -- <faces> <out folder> <prefix>"""
import bpy, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
faces, out, prefix = int(argv[0]), argv[1], argv[2]
lmat = argv[3] if len(argv) > 3 else ""          # model -> rip camera frame (rows), to straighten the gun
dim = float(argv[4]) if len(argv) > 4 else 1.0    # the Meshy colour as the game shows it (graft_build's scale)
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
for o in list(bpy.data.objects):
    if o.type == "MESH" and o.name.startswith("meshy") and len(o.data.vertices) < 100:
        bpy.data.objects.remove(o)
m = next(o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("meshy"))
mod = m.modifiers.new("dec", "DECIMATE"); mod.ratio = faces / len(m.data.polygons)
show = [m] + [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("moving")]
# the game's batched first-pass draws (depth and normals only, no colour texture) are copies of parts drawn again in
# colour: in the game they never show; here they would show as white plates. Their faces go.
import bmesh
for o in show[1:]:
    bare = {i for i, ms in enumerate(o.data.materials) if ms and ms.node_tree and
            not any(n.type == "TEX_IMAGE" and n.image for n in ms.node_tree.nodes)}
    bm = bmesh.new(); bm.from_mesh(o.data)
    gone = [f for f in bm.faces if f.material_index in bare]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    bm.to_mesh(o.data); bm.free()
    print("REMOVED", len(gone), "untextured faces (batched first-pass copies) from", o.name)
for o in bpy.data.objects:
    if o.type == "MESH" and o not in show:
        o.hide_render = True
for o in list(bpy.data.objects):
    if o.type in ("LIGHT", "CAMERA"):
        bpy.data.objects.remove(o)
if lmat:
    import numpy as np
    from mathutils import Matrix
    L = np.load(lmat)
    Q = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)   # Blender -> rip camera frame
    R = np.linalg.inv(L).T @ Q                                   # Blender -> the gun's own axes (x right, y muzzle, z up)
    R4 = Matrix([list(R[0]) + [0], list(R[1]) + [0], list(R[2]) + [0], [0, 0, 0, 1]])
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.matrix_world = R4 @ o.matrix_world
if dim != 1.0:              # darken Meshy's colour the way the game file does
    for ms in m.data.materials:
        nt = ms.node_tree
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        lk = bsdf.inputs[0].links[0] if bsdf.inputs[0].links else None
        if lk:
            mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
            mix.inputs[0].default_value = 1.0
            nt.links.new(lk.from_socket, mix.inputs[6]); mix.inputs[7].default_value = (dim, dim, dim, 1)
            nt.links.new(mix.outputs[2], bsdf.inputs[0])
dg = bpy.context.evaluated_depsgraph_get()
pts = []
for o in show:
    e = o.evaluated_get(dg)
    pts += [e.matrix_world @ Vector(c) for c in e.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
cen, size = (lo + hi) / 2, max(hi - lo)
try:
    sc.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
sc.world = bpy.data.worlds.new("w")
if sc.world.node_tree:
    bg = sc.world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.10, 0.10, 0.11, 1); bg.inputs[1].default_value = 0.6
for loc, e in (((1, -0.6, 1.2), 160), ((-1, 0.4, 0.8), 60), ((0.3, 1, -0.5), 40), ((-0.6, -1, -0.2), 35)):
    d = bpy.data.lights.new("l", "AREA"); d.energy = e * size * size; d.size = size * 2
    lo_ = bpy.data.objects.new("l", d); sc.collection.objects.link(lo_)
    lo_.location = cen + Vector(loc) * size * 2
    lo_.rotation_euler = (cen - lo_.location).to_track_quat("-Z", "Y").to_euler()
cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cd.lens = 50
L = hi.y - lo.y            # the gun's length runs along Blender Y: muzzle toward +Y, stock toward -Y (checked on the pictures)
def at(f):                 # a point f of the way from the stock end (0) to the muzzle (1)
    return Vector((cen.x, lo.y + f * L, cen.z))
views = [
    ("01_right_side", Vector((1, 0, 0)), cen, 1.0),
    ("02_left_side", Vector((-1, 0, 0)), cen, 1.0),
    ("03_top", Vector((0.0001, 0, 1)), cen, 1.0),
    ("04_underneath", Vector((0.0001, 0, -1)), cen, 1.0),
    ("05_from_behind_shoulder", Vector((0.3, -1, 0.45)), cen, 0.95),
    ("06_from_the_front", Vector((0.3, 1, 0.25)), cen, 0.95),
    ("07_three_quarter_right", Vector((1, -0.6, 0.45)), cen, 1.0),
    ("08_three_quarter_left", Vector((-1, -0.5, 0.4)), cen, 1.0),
    ("09_close_grip_and_stock", Vector((1, -0.3, 0.15)), at(0.22), 0.5),
    ("10_close_wires_and_body", Vector((1, 0.2, 0.35)), at(0.5), 0.5),
    ("11_close_join_left", Vector((-1, -0.2, 0.25)), at(0.4), 0.5),
    ("12_what_you_see_aiming", Vector((0.08, -1, 0.22)), at(0.35), 0.75),
]
for name, dv, tgt, zoom in views:
    dv = dv.normalized()
    flat = name[:2] in ("01", "02", "03", "04")      # flat-on views: no lens bending
    cd.type = "ORTHO" if flat else "PERSP"
    cd.ortho_scale = size * 1.08
    dist = size * zoom * (3.0 if flat else 1.5)
    cam.location = tgt + dv * dist
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, "%s_%s.png" % (prefix, name))
    bpy.ops.render.render(write_still=True)
    print("WROTE", name)
