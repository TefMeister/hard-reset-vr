"""Per part of a rip: which bones its vertices hang on (the game's weight pairing), vertex count and box.
python part_bones.py <rips>/<morph>"""
import os, re, sys
import numpy as np
d = sys.argv[1]
for l in open(os.path.join(d, "README.txt"), encoding="latin1"):
    mm = re.match(r"draw (\d+): skinned, .*?(\d+) vertices, start (\d+), (\d+) prims", l)
    g = re.search(r"OBJ group (\S+): (\d+) vertices.*box in metres (.*)$", l)
    if not (mm and g):
        continue
    k, numv = int(mm.group(1)), int(mm.group(2))
    raw = open(os.path.join(d, "draw_%02d_stream0.bin" % k), "rb").read()
    idx = np.frombuffer(open(os.path.join(d, "draw_%02d_indices.bin" % k), "rb").read(), dtype="<u2").astype(int)
    vb = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 32)
    used = sorted(set(i for i in idx if i < numv and i < len(vb)))
    w = vb[used, 24:28].astype(float) / 255; ind = vb[used, 28:32].astype(int)
    tally = {}
    for i in range(len(used)):
        for ib, wb in ((3, 3), (2, 2), (1, 1), (0, 0)):
            if w[i, wb] > 0.01:
                tally[ind[i, ib]] = tally.get(ind[i, ib], 0) + w[i, wb]
    top = sorted(tally.items(), key=lambda t: -t[1])[:3]
    print("start %6s prims %5s  %5s v  bones %-28s %s" % (mm.group(3), mm.group(4), g.group(2),
          " ".join("%d:%.0f" % t for t in top), g.group(3)))
