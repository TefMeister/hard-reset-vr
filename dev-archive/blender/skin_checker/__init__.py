"""Skin Checker - our own Blender add-on for bending Meshy hands and gloves on a finger rig.

Side panel (N) -> "Skin Checker":
  Stitch patches a Meshy import comes in as hundreds of separate patches; this joins them so the surface bends as one
  Hinges towards palm  moves each finger hinge towards the inside of its bend, so a bent finger keeps its thickness
  Make weights   each point of the mesh gets its pull from the finger bones (nearest finger, stretch across each
                 joint, then averaged in space so thin layers lying on each other move as one)
  Check bend     measures the bent mesh against its rest shape: overstretched or crushed spots, places the
                 surface passes through itself that it did not before bending, torn edges, and fingers going
                 thin at a bend (skin pulled in towards the bone); marks them in red
  Next spot      turns the view to the next worst spot, so each fault can be looked at in turn
  Clear marks    removes the red marks
Before weights: the mesh must be ONE connected surface. A Meshy .glb imports split into hundreds of patches along
its texture seams; stitch it first (Merge by Distance, about 0.02 mm) or the patches come apart at every bend.
Made for the Hard Reset VR gloves (2026-11-27); works on any mesh with an Armature modifier and a collection of
joint discs (one empty or mesh per joint named "<anything> <finger> <1|2|3>", +Z along the finger)."""

bl_info = {
    "name": "Skin Checker",
    "author": "Tefa and Claude",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "3D View > Sidebar (N) > Skin Checker",
    "description": "Bone weights for Meshy hands, and a check that finds stretching, clipping and torn bits when they bend",
    "category": "Rigging",
}

import bpy
from mathutils import Vector

if "check" in locals():
    import importlib
    importlib.reload(check); importlib.reload(weights)
else:
    from . import check, weights


def _props(ctx):
    return ctx.scene.skin_checker


class SkinCheckerSettings(bpy.types.PropertyGroup):
    mesh: bpy.props.PointerProperty(name="Mesh", type=bpy.types.Object, poll=lambda s, o: o.type == 'MESH')
    armature: bpy.props.PointerProperty(name="Rig", type=bpy.types.Object, poll=lambda s, o: o.type == 'ARMATURE')
    discs: bpy.props.PointerProperty(name="Joint discs", type=bpy.types.Collection)
    smooth_r: bpy.props.FloatProperty(name="Layer blend (mm)", default=12.0, min=0.0, max=20.0,
                                      description="Points this close move together, so stacked layers do not slice through each other")
    web_depth: bpy.props.FloatProperty(name="Web between fingers (mm)", default=40.0, min=0.0, max=80.0,
                                       description="How far past the big knuckle neighbouring fingers may still blend (Meshy joins touching fingers)")
    smooth_n: bpy.props.IntProperty(name="Blend passes", default=5, min=0, max=10)
    blend1: bpy.props.FloatProperty(name="Big knuckle stretch (mm)", default=10.0, min=1.0, max=30.0)
    blend2: bpy.props.FloatProperty(name="Middle joint stretch (mm)", default=7.0, min=1.0, max=30.0)
    blend3: bpy.props.FloatProperty(name="End joint stretch (mm)", default=10.0, min=1.0, max=30.0)
    stretch_max: bpy.props.FloatProperty(name="Too stretched (x)", default=1.6, min=1.05, max=10.0)
    squash_min: bpy.props.FloatProperty(name="Too crushed (x)", default=0.5, min=0.01, max=0.95)
    tear_jump: bpy.props.FloatProperty(name="Torn (pull difference)", default=0.5, min=0.05, max=1.0)
    test_pose: bpy.props.EnumProperty(name="Test pose", items=[
        ('GRIP', "Grip", "All fingers wrapped round a handle"),
        ('TRIGGER', "Trigger finger out", "Index straight, the others gripping: a gun held before firing"),
        ('FIST', "Fist", "Tight fist"),
        ('OPEN', "Open", "Rest pose, straight fingers")], default='GRIP')
    result: bpy.props.StringProperty(name="Result", default="")
    spots: bpy.props.StringProperty(default="")
    spot_i: bpy.props.IntProperty(default=-1)


def _islands(me):
    import bmesh
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    seen = [False] * len(bm.verts); n = 0
    for v in bm.verts:
        if seen[v.index]:
            continue
        n += 1; st = [v]
        while st:
            x = st.pop()
            if seen[x.index]:
                continue
            seen[x.index] = True
            st.extend(e.other_vert(x) for e in x.link_edges if not seen[e.other_vert(x).index])
    bm.free(); return n


class SKINCHK_OT_stitch(bpy.types.Operator):
    bl_idname = "skin_checker.stitch"; bl_label = "Stitch patches"
    bl_description = "Join the patches a Meshy import is split into (Merge by Distance), so the surface bends as one; the texture is kept"
    bl_options = {'REGISTER', 'UNDO'}
    dist: bpy.props.FloatProperty(name="Distance (mm)", default=0.02, min=0.0001, max=1.0)

    def execute(self, ctx):
        import bmesh
        p = _props(ctx)
        if not p.mesh:
            self.report({'ERROR'}, "Pick the mesh first"); return {'CANCELLED'}
        me = p.mesh.data; a = _islands(me); v0 = len(me.vertices)
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=self.dist / 1000); bm.to_mesh(me); bm.free()
        b = _islands(me)
        self.report({'INFO'}, f"Patches {a} -> {b}; points {v0} -> {len(me.vertices)}"); return {'FINISHED'}


class SKINCHK_OT_hinges(bpy.types.Operator):
    bl_idname = "skin_checker.hinges"; bl_label = "Hinges towards palm"
    bl_description = ("Move each finger hinge towards the inside of its bend, as a real knuckle turns: the finger keeps its "
                      "thickness when bent. 4 mm measured best on the Hard Reset right glove; its thumb tip took 6 mm more")
    bl_options = {'REGISTER', 'UNDO'}
    mm: bpy.props.FloatProperty(name="Distance (mm)", default=4.0, min=-20.0, max=20.0)
    only: bpy.props.StringProperty(name="Only bones (comma list, empty = every finger bone)", default="")

    def execute(self, ctx):
        p = _props(ctx); arm = p.armature
        if not arm:
            self.report({'ERROR'}, "Pick the rig first"); return {'CANCELLED'}
        names = [s.strip() for s in self.only.split(",") if s.strip()]
        prev = ctx.view_layer.objects.active; ctx.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='EDIT')
        for b in arm.data.edit_bones:
            if b.parent is None or (names and b.name not in names):
                continue
            roll_to = b.z_axis.copy(); b.head = b.head + b.z_axis.normalized() * (self.mm / 1000); b.align_roll(roll_to)
        bpy.ops.object.mode_set(mode='OBJECT'); ctx.view_layer.objects.active = prev
        self.report({'INFO'}, f"Hinges moved {self.mm} mm; press Make weights again"); return {'FINISHED'}


class SKINCHK_OT_weights(bpy.types.Operator):
    bl_idname = "skin_checker.weights"; bl_label = "Make weights"
    bl_description = "Give the mesh its bone weights from the rig's finger bones and the joint discs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, ctx):
        p = _props(ctx)
        if not (p.mesh and p.armature and p.discs):
            self.report({'ERROR'}, "Pick the mesh, the rig and the joint discs first"); return {'CANCELLED'}
        weights.skin_weights(p.mesh.name, p.armature.name, p.discs.name, smooth_r=p.smooth_r / 1000, smooth_n=p.smooth_n,
                             blend={1: p.blend1 / 1000, 2: p.blend2 / 1000, 3: p.blend3 / 1000}, web_depth=p.web_depth / 1000)
        if not any(m.type == 'ARMATURE' for m in p.mesh.modifiers):
            m = p.mesh.modifiers.new("bend", 'ARMATURE'); m.object = p.armature
        self.report({'INFO'}, "Weights made"); return {'FINISHED'}


POSES = {
    'GRIP': ({'1': 45, '2': 65, '3': 35}, {'1': 15, '2': 25, '3': 30}, None),
    'TRIGGER': ({'1': 45, '2': 65, '3': 35}, {'1': 15, '2': 25, '3': 30}, {'1': 5, '2': 5, '3': 0}),
    'FIST': ({'1': 70, '2': 90, '3': 60}, {'1': 25, '2': 35, '3': 40}, None),
    'OPEN': ({'1': 0, '2': 0, '3': 0}, {'1': 0, '2': 0, '3': 0}, None),
}


def apply_pose(arm, key):
    import math
    fing, thumb, index = POSES[key]
    for pb in arm.pose.bones:
        pb.rotation_mode = 'XYZ'
        if '_' not in pb.name:
            pb.rotation_euler = (0, 0, 0); continue
        f, i = pb.name.rsplit('_', 1)
        a = (thumb if f == 'thumb' else (index if (f == 'index' and index) else fing)).get(i, 0)
        pb.rotation_euler = (math.radians(a), 0, 0)
    bpy.context.view_layer.update()


class SKINCHK_OT_pose(bpy.types.Operator):
    bl_idname = "skin_checker.pose"; bl_label = "Bend into test pose"
    bl_description = "Bend the rig into the chosen test pose (curl is each bone's own X turn)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, ctx):
        p = _props(ctx)
        if not p.armature:
            self.report({'ERROR'}, "Pick the rig first"); return {'CANCELLED'}
        apply_pose(p.armature, p.test_pose); return {'FINISHED'}


class SKINCHK_OT_check(bpy.types.Operator):
    bl_idname = "skin_checker.check"; bl_label = "Check bend"
    bl_description = "Measure the bent mesh for stretching, clipping and torn edges, and mark them in red"

    def execute(self, ctx):
        p = _props(ctx)
        if not p.mesh:
            self.report({'ERROR'}, "Pick the mesh first"); return {'CANCELLED'}
        r = check.skin_check(p.mesh.name, True, p.stretch_max, p.squash_min, p.tear_jump, p.discs.name if p.discs else None)
        lo, hi = r['squash_or_stretch_worst']
        p.result = (f"stretched/crushed {r['stretch_edges']} (worst {hi}x / {lo}x) | clipping {r['clip_pairs']} | torn {r['tear_edges']}"
                    f" | thin joints {len(r['thin_joints'])} of {len(r['joint_width'])} (thinnest {r['thin_worst']}x)")
        p.spots = ";".join(",".join(str(float(x)) for x in s['centre']) for s in r['spots'][:40])
        p.spot_i = -1
        self.report({'INFO'}, p.result); return {'FINISHED'}


class SKINCHK_OT_next(bpy.types.Operator):
    bl_idname = "skin_checker.next_spot"; bl_label = "Next spot"
    bl_description = "Turn the view to the next worst fault spot"

    def execute(self, ctx):
        p = _props(ctx)
        pts = [Vector([float(x) for x in s.split(",")]) for s in p.spots.split(";") if s]
        if not pts:
            self.report({'WARNING'}, "Run Check bend first"); return {'CANCELLED'}
        p.spot_i = (p.spot_i + 1) % len(pts)
        for area in ctx.screen.areas:
            if area.type == 'VIEW_3D':
                r3 = area.spaces.active.region_3d; r3.view_location = pts[p.spot_i]; r3.view_distance = 0.08
        self.report({'INFO'}, f"Spot {p.spot_i + 1} of {len(pts)}"); return {'FINISHED'}


class SKINCHK_OT_clear(bpy.types.Operator):
    bl_idname = "skin_checker.clear"; bl_label = "Clear marks"
    bl_description = "Remove the red fault marks"

    def execute(self, ctx):
        p = _props(ctx)
        if p.mesh:
            o = bpy.data.objects.get(p.mesh.name + " faults")
            if o:
                bpy.data.objects.remove(o)
        return {'FINISHED'}


class SKINCHK_PT_panel(bpy.types.Panel):
    bl_label = "Skin Checker"; bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'; bl_category = "Skin Checker"

    def draw(self, ctx):
        p = _props(ctx); col = self.layout.column()
        col.prop(p, "mesh"); col.prop(p, "armature"); col.prop(p, "discs")
        col.operator("skin_checker.stitch", icon='AUTOMERGE_ON')
        col.operator("skin_checker.hinges", icon='BONE_DATA')
        box = col.box(); box.label(text="Weights")
        for k in ("smooth_r", "smooth_n", "web_depth", "blend1", "blend2", "blend3"):
            box.prop(p, k)
        box.operator("skin_checker.weights", icon='MOD_VERTEX_WEIGHT')
        box = col.box(); box.label(text="Test pose")
        box.prop(p, "test_pose", text=""); box.operator("skin_checker.pose", icon='POSE_HLT')
        box = col.box(); box.label(text="Check")
        for k in ("stretch_max", "squash_min", "tear_jump"):
            box.prop(p, k)
        row = box.row(); row.operator("skin_checker.check", icon='VIEWZOOM'); row.operator("skin_checker.next_spot", icon='FORWARD')
        box.operator("skin_checker.clear", icon='X')
        if p.result:
            for part in p.result.split(" | "):
                box.label(text=part)


CLASSES = (SkinCheckerSettings, SKINCHK_OT_stitch, SKINCHK_OT_hinges, SKINCHK_OT_weights, SKINCHK_OT_pose, SKINCHK_OT_check, SKINCHK_OT_next, SKINCHK_OT_clear, SKINCHK_PT_panel)


def register():
    for c in CLASSES:
        bpy.utils.register_class(c)
    bpy.types.Scene.skin_checker = bpy.props.PointerProperty(type=SkinCheckerSettings)


def unregister():
    del bpy.types.Scene.skin_checker
    for c in reversed(CLASSES):
        bpy.utils.unregister_class(c)
