# Hard Reset VR - a cyborg / cyberpunk LEFT hand, built in separate parts on a finger rig.
#
# Run:  blender -b -P cyborg_hand.py -- <out folder>
# Makes: cyborg_hand_left.blend (parts + armature + named poses), one OBJ per pose
#        (hand_left_<pose>.obj, every part its own "o" group) and preview pictures.
#
# Frame (the add-on's, hr_hands.c): metres; fingers point -Z, back of the hand +Y, thumb +X (left hand);
# the origin is the controller's grip point, which sits just in front of the palm where a handle would be.
# The right hand is the add-on's mirror of this one.
#
# Every part is its own object, parented rigidly to one bone, so a finger moves by turning its bones.
# Poses are plain bone turns (degrees about the bone's own X = curl toward the palm), kept in POSES below.

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else os.path.dirname(bpy.data.filepath or ".")
os.makedirs(OUT, exist_ok=True)

# ---- named numbers ---------------------------------------------------------------------------------------------
PALM_W, PALM_L, PALM_T = 0.084, 0.092, 0.028      # width (x), length (z), thickness (y)
PALM_CY = 0.030                                    # palm centre's y: the handle sits in front of the palm (y < 0)
PALM_CZ = 0.010                                    # palm centre's z (knuckles at PALM_CZ - PALM_L/2)
SEG_W, SEG_T = 0.0175, 0.0165                      # finger segment width and thickness
FINGERS = {                                        # name: (x at the knuckle, segment lengths base->tip)
    "index":  ( 0.029, (0.044, 0.026, 0.021)),
    "middle": ( 0.009, (0.048, 0.029, 0.023)),
    "ring":   (-0.011, (0.045, 0.027, 0.021)),
    "pinky":  (-0.030, (0.036, 0.021, 0.018)),
}
THUMB_BASE = Vector((0.034, PALM_CY - 0.010, 0.028))
THUMB_DIR = Vector((0.45, -0.30, -0.84)).normalized()
THUMB_BACK = Vector((0.6, 0.8, 0.0))                 # the thumbnail side; the thumb folds the other way, across the palm
THUMB_SEGS = (0.038, 0.030, 0.025)
WRIST_Z = PALM_CZ + PALM_L / 2

POSES = {   # bone: curl degrees for segments 1,2,3 (thumb too); spread in degrees as 4th value for fingers
    "open":    {f: (0, 0, 0) for f in list(FINGERS) + ["thumb"]},
    "relaxed": {"index": (12, 18, 10), "middle": (16, 22, 12), "ring": (20, 26, 14), "pinky": (24, 30, 16),
                "thumb": (10, 10, 8)},
    "gun_grip": {"index": (22, 28, 18),            # index along the trigger guard, tip on the trigger
                 "middle": (78, 88, 52), "ring": (82, 90, 55), "pinky": (85, 92, 55),
                 "thumb": (35, 30, 25)},
    "fist":    {"index": (85, 100, 65), "middle": (88, 100, 65), "ring": (90, 100, 65), "pinky": (92, 100, 65),
                "thumb": (45, 40, 35)},
    "point":   {"index": (0, 0, 0), "middle": (85, 100, 65), "ring": (90, 100, 65), "pinky": (92, 100, 65),
                "thumb": (40, 35, 30)},
}

# ---- scene -----------------------------------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
col = bpy.data.collections.new("CyborgHand_L"); scene.collection.children.link(col)

def mat(name, base, metal, rough, emit=None, strength=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*base, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = strength
    m.diffuse_color = (*(emit or base), 1)
    return m

M_PLATE = mat("gunmetal_plate", (0.10, 0.11, 0.12), 1.0, 0.32)
M_DARK  = mat("carbon_joint", (0.02, 0.02, 0.025), 0.4, 0.55)
M_GLOW  = mat("cyan_glow", (0.0, 0.8, 1.0), 0.0, 0.3, emit=(0.0, 0.85, 1.0), strength=6.0)
M_HOT   = mat("magenta_accent", (0.9, 0.05, 0.55), 0.2, 0.3, emit=(1.0, 0.05, 0.6), strength=3.0)
M_PAD   = mat("rubber_pad", (0.035, 0.035, 0.04), 0.0, 0.8)

def obj_from_bm(name, bm, material):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(material)
    for p in me.polygons: p.use_smooth = False
    o = bpy.data.objects.new(name, me); col.objects.link(o)
    return o

def box(name, size, material, bevel=0.0025, segs=2):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, segments=segs, affect='EDGES', profile=0.5)
    return obj_from_bm(name, bm, material)

def cyl(name, radius, depth, material, verts=16, axis='X'):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=radius, radius2=radius, depth=depth)
    rot = {'X': Matrix.Rotation(math.radians(90), 4, 'Y'), 'Y': Matrix.Rotation(math.radians(90), 4, 'X'),
           'Z': Matrix.Identity(4)}[axis]
    bmesh.ops.transform(bm, matrix=rot, verts=bm.verts)
    return obj_from_bm(name, bm, material)

def place(o, loc, rot=Matrix.Identity(3)):
    sc = Matrix.Diagonal((*o.scale, 1.0))
    o.matrix_world = Matrix.Translation(loc) @ rot.to_4x4() @ sc
    return o

# ---- armature --------------------------------------------------------------------------------------------------
arm_data = bpy.data.armatures.new("HandRig_L")
arm = bpy.data.objects.new("HandRig_L", arm_data); col.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones
root = eb.new("wrist"); root.head = (0, PALM_CY, WRIST_Z + 0.02); root.tail = (0, PALM_CY, PALM_CZ); root.roll = 0

knuckle_z = PALM_CZ - PALM_L / 2
chains = {}
for f, (x, lens) in FINGERS.items():
    head = Vector((x, PALM_CY + 0.002, knuckle_z + 0.004)); prev = root; names = []
    for i, L in enumerate(lens):
        b = eb.new(f"{f}_{i+1}"); b.head = head; b.tail = head + Vector((0, 0, -L)); b.roll = 0
        b.parent = prev; b.use_connect = i > 0; prev = b; head = b.tail.copy(); names.append(b.name)
    chains[f] = names
head = THUMB_BASE.copy(); prev = root; names = []
for i, L in enumerate(THUMB_SEGS):
    b = eb.new(f"thumb_{i+1}"); b.head = head; b.tail = head + THUMB_DIR * L
    b.align_roll(THUMB_BACK)                              # bone Z = thumbnail side, so a curl folds across the palm
    b.parent = prev; b.use_connect = i > 0; prev = b; head = b.tail.copy(); names.append(b.name)
chains["thumb"] = names
bone_frames = {b.name: (b.matrix.copy(), b.length) for b in eb}
bpy.ops.object.mode_set(mode='OBJECT')

def parent_to_bone(o, bone):
    mw = o.matrix_world.copy()
    o.parent = arm; o.parent_type = 'BONE'; o.parent_bone = bone
    bpy.context.view_layer.update()
    o.matrix_world = mw

# ---- palm parts ------------------------------------------------------------------------------------------------
parts = []
def add(o, bone): parent_to_bone(o, bone); parts.append(o); return o

add(place(box("palm_core", (PALM_W - 0.008, PALM_T - 0.006, PALM_L - 0.006), M_DARK, 0.004), (0, PALM_CY, PALM_CZ)), "wrist")
add(place(box("palm_back_plate", (PALM_W, 0.008, PALM_L * 0.78), M_PLATE, 0.003),
          (0, PALM_CY + PALM_T / 2, PALM_CZ + 0.006)), "wrist")
add(place(box("palm_back_glow_strip", (0.006, 0.0022, PALM_L * 0.55), M_GLOW, 0.0008, 1),
          (-0.012, PALM_CY + PALM_T / 2 + 0.0045, PALM_CZ + 0.004)), "wrist")
add(place(box("palm_back_vent", (0.026, 0.0025, 0.02), M_HOT, 0.0008, 1),
          (0.018, PALM_CY + PALM_T / 2 + 0.0045, PALM_CZ + 0.022)), "wrist")
add(place(box("palm_pad", (PALM_W - 0.014, 0.006, PALM_L * 0.7), M_PAD, 0.003),
          (0, PALM_CY - PALM_T / 2, PALM_CZ + 0.004)), "wrist")
add(place(box("knuckle_guard", (PALM_W + 0.004, 0.012, 0.016), M_PLATE, 0.003),
          (0, PALM_CY + PALM_T / 2 - 0.002, knuckle_z + 0.012)), "wrist")
ring = cyl("wrist_ring", 0.037, 0.026, M_DARK, 24, 'Z'); ring.scale = (1, 0.55, 1)
add(place(ring, (0, PALM_CY, WRIST_Z + 0.010)), "wrist")
band = cyl("wrist_glow_band", 0.0385, 0.004, M_GLOW, 24, 'Z'); band.scale = (1, 0.57, 1)
add(place(band, (0, PALM_CY, WRIST_Z + 0.002)), "wrist")
for side, x in (("thumb_side", 0.034), ("pinky_side", -0.034)):
    add(place(cyl(f"wrist_piston_{side}", 0.004, 0.05, M_PLATE, 10, 'Z'),
              (x, PALM_CY + 0.012, WRIST_Z - 0.012)), "wrist")

# ---- finger parts: per segment a plate, a joint drum at its base, a glow line on the back, a tip pad ------------
def seg_parts(prefix, bone, L, w, t, last):
    m, _ = bone_frames[bone]
    rot = m.to_3x3(); base = m.translation
    along = rot @ Vector((0, 1, 0)); up = rot @ Vector((0, 0, 1))      # bone Y = along, bone Z = back of the hand
    def at(a, u=0.0): return base + along * a + up * u
    # a box in the bone's frame: x across, y along, z back
    def bbox(name, sx, sa, sz, mat_, a, u, bev):
        o = box(name, (sx, sz, sa), mat_, bev)                         # built as (x, y=thick, z=long)
        r = rot @ Matrix(((1, 0, 0), (0, 0, 1), (0, 1, 0)))            # map box y->bone z (back), box z->bone y
        return add(place(o, at(a, u), r), bone)
    bbox(f"{prefix}_plate", w, L * 0.86, t, M_PLATE, L * 0.52, 0.0, 0.0028)
    bbox(f"{prefix}_glow", 0.003, L * 0.55, 0.002, M_GLOW, L * 0.5, t / 2 + 0.0008, 0.0006)
    drum = cyl(f"{prefix}_joint", t * 0.42, w * 1.08, M_DARK, 14, 'X')
    add(place(drum, at(0.0, 0.0), rot), bone)
    if last:
        bbox(f"{prefix}_tip_pad", w * 0.8, L * 0.35, 0.004, M_PAD, L * 0.7, -t / 2, 0.0015)
        bbox(f"{prefix}_tip_cap", w * 0.92, 0.006, t * 0.85, M_HOT, L * 0.95, 0.001, 0.0015)

for f, names in chains.items():
    if f == "thumb":
        widths = (0.021, 0.019, 0.017); thick = (0.019, 0.017, 0.015); lens = THUMB_SEGS
    else:
        widths = (SEG_W, SEG_W * 0.95, SEG_W * 0.9); thick = (SEG_T, SEG_T * 0.95, SEG_T * 0.9); lens = FINGERS[f][1]
    for i, bn in enumerate(names):
        seg_parts(bn, bn, lens[i], widths[i], thick[i], i == len(names) - 1)

# ---- dock markers (not exported): where things meet a weapon ---------------------------------------------------
def marker(name, loc, bone, size=0.008):
    e = bpy.data.objects.new(name, None); e.empty_display_type = 'SPHERE'; e.empty_display_size = size
    col.objects.link(e); e.location = loc; parent_to_bone(e, bone); return e
marker("DOCK_grip_point", Vector((0, 0, 0)), "wrist")
marker("DOCK_index_tip", Vector(bone_frames["index_3"][0].translation) + Vector((0, 0, -FINGERS["index"][1][2])), "index_3", 0.005)
marker("DOCK_thumb_tip", bone_frames["thumb_3"][0].translation + THUMB_DIR * THUMB_SEGS[2], "thumb_3", 0.005)
handle = cyl("REF_gun_handle", 0.016, 0.11, M_PAD, 20, 'Z')        # a pistol handle, not exported
handle.matrix_world = Matrix.Translation((0, -0.004, 0.0)) @ Matrix.Rotation(math.radians(-18), 4, 'X')
handle.display_type = 'WIRE'; handle.hide_render = True

# ---- poses -----------------------------------------------------------------------------------------------------
def set_pose(name):
    for f, names in chains.items():
        curls = POSES[name].get(f, (0, 0, 0))
        for bn, deg in zip(names, curls):
            pb = arm.pose.bones[bn]; pb.rotation_mode = 'XYZ'
            pb.rotation_euler = (math.radians(-deg), 0, 0)    # bone X: negative turns toward the palm (-Y)
    bpy.context.view_layer.update()

# store each pose as an action with one frame, so the .blend carries them for Tefa
arm.animation_data_create()
for i, pname in enumerate(POSES):
    set_pose(pname)
    act = bpy.data.actions.new(f"pose_{pname}"); act.use_fake_user = True
    arm.animation_data.action = act
    for pb in arm.pose.bones:
        pb.keyframe_insert("rotation_euler", frame=1)
arm.animation_data.action = None

# ---- export one OBJ per pose -----------------------------------------------------------------------------------
def export(pname):
    set_pose(pname)
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.wm.obj_export(filepath=os.path.join(OUT, f"hand_left_{pname}.obj"), export_selected_objects=True,
                          forward_axis='Y', up_axis='Z', export_triangulated_mesh=True, export_normals=True,
                          export_uv=False, export_materials=True, export_object_groups=False,
                          apply_modifiers=True)

for pname in POSES: export(pname)

# ---- the add-on's finger rig (hr_hands_rig.c): one pivot per segment, axis so a positive turn folds to the palm ----
MAX_DEG = {"thumb": (45, 45, 60)}
with open(os.path.join(OUT, "hand_left.pivots"), "w") as fp:
    fp.write("# Hard Reset VR cyborg hand (left): pivot <segment> x y z ax ay az max_deg; rest pose = open hand" + chr(10))
    fp.write("palm 0 -1 0" + chr(10))
    for f, names in chains.items():
        for i, bn in enumerate(names):
            m, _ = bone_frames[bn]
            h = m.translation; ax = -(m.to_3x3() @ Vector((1, 0, 0)))
            mx = MAX_DEG.get(f, (90, 100, 70))[i]
            fp.write(f"pivot {bn} {h.x:.5f} {h.y:.5f} {h.z:.5f} {ax.x:.4f} {ax.y:.4f} {ax.z:.4f} {mx}" + chr(10))

# ---- preview pictures ------------------------------------------------------------------------------------------
scene.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x, scene.render.resolution_y = 900, 900
scene.render.film_transparent = False
world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND"); bg.inputs[0].default_value = (0.012, 0.012, 0.02, 1)
for loc, energy in (((0.3, 0.4, 0.3), 30), ((-0.3, -0.2, 0.2), 12), ((0, 0.1, -0.4), 10)):
    ld = bpy.data.lights.new("L", 'AREA'); ld.energy = energy; ld.size = 0.3
    lo = bpy.data.objects.new("L", ld); col.objects.link(lo); lo.location = loc
    lo.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new("cam"); cd.lens = 50; cam = bpy.data.objects.new("cam", cd); col.objects.link(cam)
scene.camera = cam
VIEWS = {"back": Vector((0.12, 0.30, -0.02)), "palm": Vector((0.10, -0.30, 0.02)), "side": Vector((0.32, 0.05, -0.05))}
centre = Vector((0, PALM_CY - 0.005, -0.015))
for pname in ("open", "gun_grip", "fist"):
    set_pose(pname)
    for vname, off in VIEWS.items():
        cam.location = centre + off
        cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = os.path.join(OUT, f"preview_{pname}_{vname}.png")
        bpy.ops.render.render(write_still=True)

set_pose("relaxed")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "cyborg_hand_left.blend"))
print("PARTS", len(parts), "BONES", len(arm.pose.bones), "POSES", list(POSES))
