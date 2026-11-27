"""Which parts of a gun stay put in all five morphs (the base frame) and which move or come and go (morph parts).
A part = one skinned draw, named by its index range (start, prims); 'stays put' = present in every morph with every
vertex within TOL of where it is in morph 1. Prints the lists and writes <out>/<gun>_parts.json.
python base_parts.py <rips folder> <out folder>"""
import json, os, re, sys
import numpy as np

rips, out = sys.argv[1], sys.argv[2]
TOL = 0.002   # metres
os.makedirs(out, exist_ok=True)


def parts(m):
    d = os.path.join(rips, m)
    key = {}
    for l in open(os.path.join(d, "README.txt"), encoding="latin1"):
        mm = re.match(r"draw (\d+): skinned, .*?start (\d+), (\d+) prims", l)
        g = re.search(r"OBJ group (\S+):", l)
        if mm and g:
            key[g.group(1)] = (int(mm.group(2)), int(mm.group(3)))
    verts, cur = {}, None
    for l in open(os.path.join(d, "gun.obj"), encoding="latin1"):
        if l.startswith("g "):
            cur = l.split(None, 1)[1].strip()
        elif l.startswith("v ") and cur in key:
            verts.setdefault(cur, []).append([float(t) for t in l.split()[1:4]])
    res = {}
    for g, v in verts.items():
        v = np.array(v)
        if v[:, 0].max() < 0 or v[:, 2].max() > -0.1:      # the HUD dial and the crosshair
            continue
        res[key[g]] = (g, v)
    return res


for gun in ("cln", "nrg"):
    ms = ["%s%d" % (gun, i) for i in range(1, 6)]
    P = {m: parts(m) for m in ms}
    # each morph lined up on morph 1 by a rigid fit over the parts they share, refitted on the parts that agree
    ref = P[ms[0]]
    def kabsch(A, B):
        ca, cb = A.mean(0), B.mean(0)
        U, _, Vt = np.linalg.svd((A - ca).T @ (B - cb))
        D = np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))])
        R = U @ D @ Vt
        return R, cb - ca @ R
    err = {}
    for m in ms[1:]:
        common = [k for k in ref if k in P[m] and P[m][k][1].shape == ref[k][1].shape]
        use = common
        for it in range(6):
            A = np.vstack([P[m][k][1] for k in use]); B = np.vstack([ref[k][1] for k in use])
            R, T = kabsch(A, B)
            e = {k: np.abs(P[m][k][1] @ R + T - ref[k][1]).max() for k in common}
            keep = [k for k in common if e[k] < max(TOL, np.median(list(e.values())) * 1.5)]
            if keep == use or len(keep) < 3: break
            use = keep
        err[m] = e
        if gun == "nrg": print("   ", m, " ".join("%d:%.3f" % (k[0] % 100000, e[k]) for k in sorted(e, key=lambda k: e[k])))
        print("  %s: lined up on %d of %d shared parts" % (m, len(use), len(common)))
    base, moving = [], []
    for k, (g, v) in ref.items():
        ok = all(k in err[m] and err[m][k] < TOL for m in ms[1:])
        (base if ok else moving).append(k)
    extra = sorted({k for m in ms[1:] for k in P[m] if k not in P[ms[0]]})
    groups = {m: {"base": [P[m][k][0] for k in base if k in P[m]],
                  "moving": [P[m][k][0] for k in P[m] if k not in base]} for m in ms}
    json.dump({"base": base, "moving_in_morph1": moving, "only_in_other_morphs": extra, "groups": groups},
              open(os.path.join(out, "%s_parts.json" % gun), "w"), indent=1)
    nb = sum(len(P[ms[0]][k][1]) for k in base)
    print("%s: %d base parts (%d vertices), %d moving in morph 1, %d only in other morphs; per morph moving: %s"
          % (gun, len(base), nb, len(moving), len(extra), ", ".join("%s %d" % (m, len(groups[m]["moving"])) for m in ms)))
