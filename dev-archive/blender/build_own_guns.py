"""Our own whole guns in place of the game's morphs (2026-11-28, first try: cln1 rifle, cln2 shotgun).
<name>_local.obj (gun-local metres: right, ahead with 0 at the muzzle tip, up from the barrel line) -> the camera frame
of that morph's rip, the muzzle tip on the game gun's muzzle; then graft_build.py with EVERY game gun part hidden.
python build_own_guns.py   -> work/graft/gun_graft_<morph>.bin and the lines for d3d9_vr.ini"""
import os, re, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RIPS = r"D:\SteamLibrary\steamapps\common\HardReset\rips"
GB = os.path.expanduser("~/github-backups/staging/hard-reset-vr/proxy-d3d9/tools/graft_build.py")
ANCHOR = (45663, 182)
FRONT_M = 0.05                       # the game gun's front slice that gives its barrel line
# name, morph, grip (right, ahead, up) and off-hand spot in gun-local metres
GUNS = [
    ("rifle", "cln1", 0.4204, (0.0, -(0.38 + 0.953), (-0.14 - 0.186)), (0.0, -(-0.40 + 0.953), (0.04 - 0.186))),
    ("shotgun", "cln2", 0.4467, (0.0, -(0.37 + 0.952), (-0.08 - 0.247)), (0.0, -(-0.55 + 0.952), (0.03 - 0.247))),
]
out = os.path.join(HERE, "graft")
os.makedirs(out, exist_ok=True)
for name, morph, s, grip_l, off_l in GUNS:
    d = os.path.join(RIPS, morph)
    groups, cur = {}, None
    for l in open(os.path.join(d, "gun.obj"), encoding="latin1"):
        if l.startswith("g "):
            cur = l.split(None, 1)[1].strip(); groups[cur] = []
        elif l.startswith("v "):
            groups[cur].append([float(t) for t in l.split()[1:4]])
    groups = {k: np.array(v) for k, v in groups.items() if v}
    gun = {k: v for k, v in groups.items() if not (v[:, 0].max() < 0 or v[:, 2].max() > -0.1)}   # not the dial, not the crosshair
    an = None
    for l in open(os.path.join(d, "README.txt"), encoding="latin1"):
        m = re.match(r"draw (\d+): skinned, .*?(\d+) vertices, start %d, %d prims" % ANCHOR, l)
        g = re.search(r"OBJ group (\S+): (\d+) vertices", l)
        if m and g:
            an = (int(m.group(1)), int(m.group(2)), g.group(1)); break
    raw = open(os.path.join(d, "draw_%02d_stream0.bin" % an[0]), "rb").read()
    idx = np.frombuffer(open(os.path.join(d, "draw_%02d_indices.bin" % an[0]), "rb").read(), dtype="<u2").astype(int)
    order, seen = [], set()
    for v in idx:
        if v < an[1] and v not in seen:
            seen.add(v); order.append(v)
    model = np.frombuffer(raw, dtype="<f2").reshape(-1, 16)[order, :3].astype(float)
    Aff, *_ = np.linalg.lstsq(np.hstack([model, np.ones((len(model), 1))]), groups[an[2]], rcond=None)
    ax = Aff[:3] / np.linalg.norm(Aff[:3], axis=1, keepdims=True)      # rows: the gun's right, muzzle, up in the camera frame
    own = np.vstack(list(gun.values())) @ ax.T
    m_tip = own[:, 1].max()
    front = own[own[:, 1] > m_tip - FRONT_M]
    r0, u0 = (front[:, 0].min() + front[:, 0].max()) / 2, (front[:, 2].min() + front[:, 2].max()) / 2
    origin = np.array([r0, m_tip, u0])
    def to_cam(p):
        return (np.asarray(p, float) + origin) @ ax
    print("%s -> %s: game muzzle tip %.3f m ahead, barrel line right %.3f up %.3f (front slice %d vertices, %.3f x %.3f m)"
          % (name, morph, m_tip, r0, u0, len(front), np.ptp(front[:, 0]), np.ptp(front[:, 2])))
    src = os.path.join(HERE, name + "_local.obj")
    dst = os.path.join(out, "own_%s.obj" % morph)
    with open(dst, "w", newline="\n") as f:
        for l in open(src):
            if l.startswith("v "):
                p = to_cam([float(t) for t in l.split()[1:4]])
                f.write("v %.6f %.6f %.6f\n" % tuple(p))
            else:
                f.write(l)
    grip_l, off_l = np.array(grip_l) * s, np.array(off_l) * s     # model units -> metres
    grip, off = to_cam(grip_l), to_cam(off_l)
    ahead, up = grip_l[1], grip_l[2]
    print("  [pose.%s] gun_grip = %.3f %.3f %.3f   foregrip_ahead_m=%.3f foregrip_up_m=%.3f"
          % (morph, grip[0], grip[1], grip[2], off_l[1] - ahead, off_l[2] - up))
    r = subprocess.run([sys.executable, GB, RIPS, morph, "%d,%d" % ANCHOR, dst, "0,0,0", out, "--keep-uv",
                        "--hide", ",".join(sorted(gun)), "--tex", HERE, "--tex-prefix", name])
    if r.returncode:
        sys.exit("graft_build failed for " + morph)
