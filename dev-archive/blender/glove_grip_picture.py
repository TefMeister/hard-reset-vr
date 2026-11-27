"""Hard Reset VR: pictures of a slimmed glove in the grip pose, with the grip spots glove_export.py found, for choosing
the controller's grip point (2026-11-27, /pd). Run headless on the game .blend glove_export.py saved:
    blender -b meshy_hand_<side>_game.blend -P glove_grip_picture.py -- <side> <hand_<side>_report.json> <out folder>
Writes grip_<side>_tube.png (a slice through the glove at the grip point, looking down the tube the fingers wrap) and grip_<side>_palm.png
(looking at the palm). Red ball = the fitted tube centre, green = the roomiest spot near it, the blue rod = the tube
axis through the red ball, the yellow ring = a 35 mm-wide stand-in for a controller handle round that axis."""
import bpy, sys, os, json, math
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
SIDE, REPORT, OUT = argv[0], argv[1], argv[2]
os.makedirs(OUT, exist_ok=True)
L = "R" if SIDE == "right" else "L"
rep = json.load(open(REPORT))
g = rep["grip"]
import skin_checker
arm = bpy.data.objects[f"HandRig_{L}"]
skin_checker.apply_pose(arm, 'GRIP')
glove = next(o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(f"{L} glove game"))
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not glove:
        o.hide_render = True
glove.hide_render = False

sc = bpy.context.scene
X, Y, Z = (Vector(a) for a in g["axes_blend_XYZ"])
circle = Vector(g["centre_blend"]); room = Vector(g["roomiest_spot_blend"])


def mat(name, rgba):
    m = bpy.data.materials.new(name); m.diffuse_color = rgba
    return m


def ball(name, at, rgba, r=0.004):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=at)
    o = bpy.context.object; o.name = name; o.data.materials.append(mat(name, rgba)); o.show_in_front = True
    return o


def rod(name, at, axis, radius, length, rgba):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=at)
    o = bpy.context.object; o.name = name
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = axis.to_track_quat('Z', 'Y')
    o.data.materials.append(mat(name, rgba))
    return o


ball("circle centre", circle, (1, 0, 0, 1))
ball("roomiest", room, (0, 1, 0, 1))
rod("tube axis", circle, Z, 0.0015, 0.16, (0.1, 0.3, 1, 1))
bpy.ops.mesh.primitive_torus_add(major_radius=0.0175, minor_radius=0.0007, location=circle)
h = bpy.context.object; h.name = "handle 35mm"
h.rotation_mode = 'QUATERNION'; h.rotation_quaternion = Z.to_track_quat('Z', 'Y')
h.data.materials.append(mat("handle", (1, 0.85, 0.1, 1)))

for e in ('BLENDER_WORKBENCH', 'BLENDER_WORKBENCH_NEXT', 'WORKBENCH'):   # the enum under-reports: try each
    try:
        sc.render.engine = e; break
    except TypeError:
        pass
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'
sc.render.resolution_x = sc.render.resolution_y = 900
cam_d = bpy.data.cameras.new("cam"); cam_d.type = 'ORTHO'; cam_d.ortho_scale = 0.16
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam


CAM_DIST = 0.5


def shot(path, look_dir, up, cut=False):
    """cut: the camera's near clip at the grip point, so the picture is a slice through the glove there"""
    cam.location = circle - look_dir.normalized() * CAM_DIST
    cam_d.clip_start = CAM_DIST - 0.0005 if cut else 0.01
    cam_d.clip_end = CAM_DIST + 0.3
    cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = look_dir.to_track_quat('-Z', 'Y')
    rot = cam.rotation_quaternion.to_matrix()
    # roll so that `up` is up on the picture
    cu = rot @ Vector((0, 1, 0)); cf = rot @ Vector((0, 0, -1))
    upp = (up - cf * up.dot(cf)).normalized()
    ang = cu.angle(upp)
    if cu.cross(upp).dot(cf) < 0:
        ang = -ang
    cam.rotation_quaternion = (Matrix.Rotation(ang, 3, cf) @ rot).to_quaternion()
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# down the tube from the index side (the grip's -Z points that way), grip +Y up
shot(os.path.join(OUT, f"grip_{SIDE}_tube.png"), Z, Y, cut=True)

# the glove's outline where each finger wraps the tube (a plane square to the tube through each finger's circle centre),
# drawn as lines with the glove hidden: index red-ish ... pinky blue-ish; the handle ring and the two spots on top
import bmesh
dg = bpy.context.evaluated_depsgraph_get()
posed = bpy.data.meshes.new_from_object(glove.evaluated_get(dg))
cols = [(1, 0.3, 0.3, 1), (1, 0.7, 0.2, 1), (0.3, 1, 0.4, 1), (0.3, 0.6, 1, 1)]
for k, cen in enumerate(g["centres"]):
    bm = bmesh.new(); bm.from_mesh(posed); bm.transform(glove.matrix_world)
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=Vector(cen), plane_no=Z)
    cut = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
    cd = bpy.data.curves.new(f"slice {k}", 'CURVE'); cd.dimensions = '3D'; cd.bevel_depth = 0.0005
    for e in cut:
        sp = cd.splines.new('POLY'); sp.points.add(1)
        for i, v in enumerate(e.verts):
            # every slice moved onto the grip point's plane, so they lie over each other in the picture
            p = v.co - Z * (Vector(cen) - circle).dot(Z)
            sp.points[i].co = (p.x, p.y, p.z, 1)
    bm.free()
    co = bpy.data.objects.new(f"slice {k}", cd); sc.collection.objects.link(co)
    cd.materials.append(mat(f"slice {k}", cols[k]))
glove.hide_render = True
shot(os.path.join(OUT, f"grip_{SIDE}_slices.png"), Z, Y)
glove.hide_render = False
for o in [o for o in bpy.data.objects if o.name.startswith("slice ")]:
    o.hide_render = True
# at the palm: looking along the grip's X towards the hand, from the palm's side
palm_side = X if SIDE == 'right' else -X          # right: +X goes INTO the palm, so the palm faces -X; left: +X away
shot(os.path.join(OUT, f"grip_{SIDE}_palm.png"), palm_side, Y)
print("PICTURES", OUT)
