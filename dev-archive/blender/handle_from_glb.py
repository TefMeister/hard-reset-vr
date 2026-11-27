"""handle_from_glb.py - one of Tefa's Meshy handle models (a .glb) -> a light OBJ the Hard Reset VR add-on can draw
(2026-11-27). Run headless:

    blender -b -P handle_from_glb.py -- <in.glb> <out folder> <name> [triangles=6000] [length_m=0.42]

What it does: imports the glb, joins it, bakes the texture's colour into the vertex colours (so the add-on, which draws
without textures, still shows the cyberpunk colours), decimates to about <triangles>, turns it so the muzzle points
forward (Blender +Y, which the OBJ exporter writes as -Z) and up is up, scales it to <length_m> long, puts the middle of
its back end at the origin, and writes <name>.obj (+ "v x y z r g b" colours) and <name>.blend. Prints the sizes.
The model's own axes as Meshy made them (checked from renders 2026-11-27): length along X, muzzle toward -X, up +Z."""
import bpy, bmesh, sys, os, math, mathutils

argv = sys.argv[sys.argv.index("--") + 1:]
src, outdir, name = argv[0], argv[1], argv[2]
target_tris = int(argv[3]) if len(argv) > 3 else 6000
length_m = float(argv[4]) if len(argv) > 4 else 0.42
os.makedirs(outdir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1: bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = ob.data

# ---- colour from the texture into a per-corner colour attribute (sampled at each corner's UV) ----
img = None
for mat in me.materials:
    if mat and mat.use_nodes:
        bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf and bsdf.inputs[0].is_linked:
            node = bsdf.inputs[0].links[0].from_node
            if node.type == "TEX_IMAGE": img = node.image
if img:
    w, h = img.size
    px = list(img.pixels[:])
    uv = me.uv_layers.active.data
    col = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    for i, l in enumerate(uv):
        u, v = l.uv
        x = min(w - 1, max(0, int((u % 1.0) * w))); y = min(h - 1, max(0, int((v % 1.0) * h)))
        k = 4 * (y * w + x)
        col.data[i].color = (px[k], px[k + 1], px[k + 2], 1.0)
    print("COLOUR from", img.name, w, h)
else:
    print("COLOUR none found")

# ---- fewer triangles ----
me.calc_loop_triangles(); before = len(me.loop_triangles)
mod = ob.modifiers.new("dec", "DECIMATE"); mod.ratio = min(1.0, target_tris / max(1, before))
bpy.ops.object.modifier_apply(modifier=mod.name)
me.calc_loop_triangles(); after = len(me.loop_triangles)

# ---- muzzle forward (-Y), up +Z, length_m long, the middle of the back end at the origin ----
# on the mesh itself (the importer may leave parents or transforms that transform_apply misses)
me.transform(ob.matrix_world); ob.matrix_world = mathutils.Matrix.Identity(4); ob.parent = None
me.transform(mathutils.Matrix.Rotation(math.radians(-90), 4, "Z"))  # -X (muzzle) -> +Y: the OBJ exporter writes Blender +Y as -Z (checked 2026-11-27)
vs = [v.co for v in me.vertices]
lo = mathutils.Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
hi = mathutils.Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
s = length_m / (hi.y - lo.y)
me.transform(mathutils.Matrix.Scale(s, 4))
vs = [v.co for v in me.vertices]
lo = mathutils.Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
hi = mathutils.Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
back = mathutils.Vector(((lo.x + hi.x) / 2, lo.y, (lo.z + hi.z) / 2))
for v in me.vertices: v.co -= back
ob.name = name

# per-vertex colour for the OBJ (the exporter writes point colours): average the corners
if img:
    pcol = me.color_attributes.new("PCol", "FLOAT_COLOR", "POINT")
    acc = [[0.0, 0.0, 0.0, 0] for _ in me.vertices]
    c = me.color_attributes["Col"].data
    for loop in me.loops:
        a = acc[loop.vertex_index]; cc = c[loop.index].color
        a[0] += cc[0]; a[1] += cc[1]; a[2] += cc[2]; a[3] += 1
    for i, a in enumerate(acc):
        n = max(1, a[3]); pcol.data[i].color = (a[0] / n, a[1] / n, a[2] / n, 1.0)
    me.color_attributes.active_color = pcol

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(outdir, name + ".blend"))
bpy.ops.wm.obj_export(filepath=os.path.join(outdir, name + ".obj"), export_selected_objects=False, export_materials=False,
                      export_uv=False, export_normals=True, export_colors=bool(img), forward_axis="NEGATIVE_Z", up_axis="Y")
size = hi - lo
print("TRIS before %d after %d; size x %.3f (wide) y %.3f (long) z %.3f (tall) m" % (before, after, size.x, size.y, size.z))
print("DONE", os.path.join(outdir, name + ".obj"))
