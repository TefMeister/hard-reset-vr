"""Skin Checker, the weights: give a Meshy glove its bone weights from the hand rig's bones.
Used by the add-on's "Make weights" button; from a script: from skin_checker.weights import skin_weights.

How a point of the glove is weighted:
  1. it belongs to the finger whose bone line is nearest (within that finger's radius, fading out over the
     last 8 mm), else to the hand;
  2. along the finger, it moves from one bone to the next across each joint's cut plane, over BLEND metres
     either side (wider at the big knuckle, where the bend is biggest);
  3. then every weight is averaged with all points within SMOOTH_R in SPACE (not along the surface), SMOOTH_N
     times. Meshy shells have separate thin layers lying on each other (the leather edge of a fingerless glove
     on the skin); averaging in space makes the layers move as one instead of slicing through each other.
The joint planes come from the "cut discs" collection (the disc's +Z is the finger's direction)."""
import bpy, numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

RAD = {'index': 0.022, 'middle': 0.022, 'ring': 0.022, 'pinky': 0.021, 'thumb': 0.024}
BLEND = {1: 0.010, 2: 0.007, 3: 0.006}
SMOOTH_R = 0.012
SMOOTH_N = 5
WEB_DEPTH = 0.040   # past the big knuckle by more than this, a finger no longer blends with its neighbours
                    # (Meshy joins touching fingers along their sides; 40 mm took tears 167 -> 0 on the right glove)


def _sm(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def skin_weights(mesh_name, arm_name, discs_coll, smooth_r=SMOOTH_R, smooth_n=SMOOTH_N, blend=BLEND, web_depth=WEB_DEPTH):
    g = bpy.data.objects[mesh_name]; arm = bpy.data.objects[arm_name]; me = g.data
    planes = {o.name[4:]: (np.array(o.matrix_world.translation), np.array((o.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()))
              for o in bpy.data.collections[discs_coll].objects}
    bones = arm.data.bones
    fingers = ('index', 'middle', 'ring', 'pinky', 'thumb')
    chains = {f: [np.array(bones[f'{f}_{i}'].head_local) for i in (1, 2, 3)] + [np.array(bones[f'{f}_3'].tail_local)] for f in fingers}
    n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)

    def linedist(c):
        d = np.full(n, 9.0)
        for a, b in zip(c[:-1], c[1:]):
            ab = b - a; t = np.clip(((co - a) @ ab) / (ab @ ab), 0, 1); q = a + t[:, None] * ab
            d = np.minimum(d, np.linalg.norm(co - q, axis=1))
        return d
    names = ['hand'] + [f'{f}_{i}' for f in fingers for i in (1, 2, 3)]
    W = np.zeros((n, len(names))); W[:, 0] = 1.0
    dist = {f: linedist(c) for f, c in chains.items()}
    owner = np.argmin(np.stack([dist[f] - RAD[f] for f in fingers]), axis=0)
    for fi, f in enumerate(fingers):
        m = (owner == fi) * (1 - _sm((dist[f] - (RAD[f] - 0.004)) / 0.008))
        s = [_sm(((co - planes[f'{f} {i}'][0]) @ planes[f'{f} {i}'][1]) / (2 * blend[i]) + 0.5) for i in (1, 2, 3)]
        for i, w in enumerate([s[0] - s[1], s[1] - s[2], s[2]]):
            W[:, names.index(f'{f}_{i + 1}')] = np.clip(w, 0, 1) * m
        W[:, 0] -= s[0] * m
    W = np.clip(W, 0, 1)
    if smooth_n and smooth_r > 0:
        kd = KDTree(n)
        for i, c in enumerate(co):
            kd.insert(c, i)
        kd.balance()
        # a point is averaged with its neighbours in space, but never across from one finger to another
        # (only finger <-> hand), so a bent finger does not drag the one beside it
        near = np.stack([dist[f] for f in fingers]).min(axis=0) < (np.array([RAD[f] for f in fingers])[owner] + 0.010)
        # depth past its own finger's big knuckle: the web between fingers (near the knuckle) may blend across
        depth = np.empty(n)
        for fi, f in enumerate(fingers):
            sel = owner == fi
            depth[sel] = (co[sel] - planes[f'{f} 1'][0]) @ planes[f'{f} 1'][1]
        grp = np.where(near & (depth > web_depth), owner, -1)
        nb = []
        for i, c in enumerate(co):
            ix = np.array([j for _, j, _ in kd.find_range(c, smooth_r)])
            if grp[i] >= 0:
                ix = ix[(grp[ix] == grp[i]) | (grp[ix] == -1)]
            nb.append(ix)
        for _ in range(smooth_n):
            W = np.array([W[ix].mean(axis=0) for ix in nb])
    W /= np.maximum(W.sum(axis=1, keepdims=True), 1e-9)
    g.vertex_groups.clear()
    for k, nm in enumerate(names):
        vg = g.vertex_groups.new(name=nm)
        for i in np.where(W[:, k] > 0.001)[0]:
            vg.add([int(i)], float(W[i, k]), 'REPLACE')
    return {nm: int((W[:, k] > 0.001).sum()) for k, nm in enumerate(names)}
