"""Fit Meshy's model onto our base frame + handle: its long axis onto ours (both ways round, four rolls), scaled to the
same length, then position and scale refined by nearest-point matching (ICP with scale); prints the match and renders
it with the game's moving parts. Saves the fitted model as a .blend.
blender -b --factory-startup -P meshy_fit.py -- <meshy.glb> <base_with_handle.glb> <moving.glb> <png prefix> <out.blend>"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
meshy_p, base_p, mov_p, png, out_blend = argv
bpy.ops.wm.read_factory_settings(use_empty=True)
rng = np.random.default_rng(1)


def imp(p, name):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=p)
    objs = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    for o in objs:
        o.name = name + "_" + o.name
    return objs


def pts(objs, n):
    a = np.vstack([np.array([(o.matrix_world @ v.co)[:] for v in o.data.vertices]) for o in objs])
    return a[rng.choice(len(a), min(n, len(a)), replace=False)]


def nearest(A, B):
    """for each row of A, the nearest row of B (brute force in chunks)"""
    out = np.empty(len(A), dtype=int); d = np.empty(len(A))
    for i in range(0, len(A), 500):
        q = A[i:i + 500]
        dd = ((q[:, None, :] - B[None, :, :]) ** 2).sum(-1)
        out[i:i + 500] = dd.argmin(1); d[i:i + 500] = dd.min(1)
    return out, np.sqrt(d)


meshy = imp(meshy_p, "meshy")
base = imp(base_p, "base")
mov = imp(mov_p, "moving")
M0 = pts(meshy, 3000)
B = pts(base, 3000)
mc, bc = M0.mean(0), B.mean(0)
ml = M0.max(0) - M0.min(0); bl = B.max(0) - B.min(0)
ma, ba = int(np.argmax(ml)), int(np.argmax(bl))
s0 = bl[ba] / ml[ma]
print("meshy box", ml.round(3), "base box", bl.round(3), "start scale %.3f" % s0)


def axis_map(ma, ba, sign, roll):
    """rotation taking meshy axis ma to base axis ba (times sign), then a roll about ba"""
    R = np.zeros((3, 3))
    others_m = [i for i in range(3) if i != ma]; others_b = [i for i in range(3) if i != ba]
    R[ba, ma] = sign
    c = [(1, 0, 0, 1), (0, -1, 1, 0), (-1, 0, 0, -1), (0, 1, -1, 0)][roll]
    R[others_b[0], others_m[0]] = c[0]; R[others_b[0], others_m[1]] = c[1]
    R[others_b[1], others_m[0]] = c[2]; R[others_b[1], others_m[1]] = c[3]
    if np.linalg.det(R) < 0:
        R[others_b[1]] *= -1
    return R


best = None
for sign in (1, -1):
    for roll in range(4):
        R = axis_map(ma, ba, sign, roll)
        s, t = s0, bc - s0 * (R @ mc)
        for it in range(25):
            P = (s * (R @ M0.T)).T + t
            idx, d = nearest(P, B)
            keep = d < np.percentile(d, 80)
            A, Bt = M0[keep], B[idx[keep]]
            # similarity fit (Umeyama) A -> Bt
            ca, cb = A.mean(0), Bt.mean(0)
            X, Y = A - ca, Bt - cb
            U, S, Vt = np.linalg.svd(Y.T @ X)
            Dg = np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))])
            R = U @ Dg @ Vt
            s = (S * np.diag(Dg)).sum() / (X ** 2).sum()
            t = cb - s * (R @ ca)
        P = (s * (R @ M0.T)).T + t
        _, d1 = nearest(P, B)
        _, d2 = nearest(B, P)
        score = np.median(d1) + np.median(d2)
        print("sign %+d roll %d: scale %.3f, median gaps %.1f / %.1f mm" % (sign, roll, s, np.median(d1) * 1000, np.median(d2) * 1000))
        if best is None or score < best[0]:
            best = (score, R, s, t, np.median(d1), np.median(d2), np.percentile(d2, 90))
score, R, s, t, g1, g2, g90 = best
print("BEST: scale %.3f (Meshy model is %.2fx the game size), median gap Meshy->ours %.1f mm, ours->Meshy %.1f mm, 90%% of "
      "ours within %.1f mm" % (s, 1 / s, g1 * 1000, g2 * 1000, g90 * 1000))
T = Matrix.Identity(4)
for i in range(3):
    for j in range(3):
        T[i][j] = s * R[i, j]
    T[i][3] = t[i]
for o in meshy:
    o.matrix_world = T @ o.matrix_world
for o in base:
    o.hide_render = True; o.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=out_blend)

sc = bpy.context.scene
try:
    sc.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1200, 700
sc.world = bpy.data.worlds.new("w")
bgn = sc.world.node_tree.nodes.get("Background") if sc.world.node_tree else None
if bgn:
    bgn.inputs[0].default_value = (0.22, 0.22, 0.24, 1); bgn.inputs[1].default_value = 1.5
allp = np.vstack([B, (s * (R @ M0.T)).T + t])
cen = Vector(allp.mean(0)); size = float((allp.max(0) - allp.min(0)).max())
for loc, e in (((1, -0.5, 1.2), 300), ((-1, 0.5, 0.6), 150), ((1, 0.5, -0.4), 100)):
    d = bpy.data.lights.new("l", "AREA"); d.energy = e * size * size; d.size = size * 2
    lo = bpy.data.objects.new("l", d); sc.collection.objects.link(lo)
    lo.location = cen + Vector(loc) * size * 2
    lo.rotation_euler = (cen - lo.location).to_track_quat("-Z", "Y").to_euler()
cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cd.type = "ORTHO"; cd.ortho_scale = size * 1.1
for name, dv in (("side", Vector((1, 0, 0.05))), ("angle", Vector((1, -0.7, 0.5)))):
    cam.location = cen + dv.normalized() * size * 3
    cam.rotation_euler = (cen - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = "%s_%s.png" % (png, name)
    bpy.ops.render.render(write_still=True)
    print("WROTE", sc.render.filepath)
