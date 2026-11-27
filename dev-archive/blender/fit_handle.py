"""fit_handle.py - fit one of our handles (handle_from_glb.py output) onto the back of a ripped Hard Reset gun
(hr_rip.c output), 2026-11-27.

    python fit_handle.py <rips folder> <morph> <handle.obj> <grip_z> <grip_y> <out folder> [--overlap 0.03] [--lift 0.02]

Both OBJs are in the same axes: x right, y up, -z ahead, metres. The ripped gun is in the game camera's frame (where
the game holds it); the handle has its back end (the stock's butt) at its origin and its muzzle end at z = -length.

The fit: the handle's FRONT-TOP corner (the top of its muzzle end, where Meshy's model would meet a receiver) is put
on the gun's REAR-BOTTOM edge (the bottom of the gun's back end, centred left-right), pushed --overlap metres into
the gun and --lift up, so the two read as one piece. Then:
  - gun_handle_<morph>.obj: the handle moved so its PISTOL GRIP (grip_z, grip_y in the handle's own coordinates; the
    middle of the grip, x = 0) is the origin: the add-on draws it at the gun's grip point;
  - <morph>.gun_grip.txt: "gun_grip = x y z", that grip in the game camera's frame, for d3d9_vr.ini [pose.<morph>]
    (the gun mover then puts exactly that spot at the controller);
  - preview_<morph>.obj: the gun and the handle together, in the gun's frame, for Blender and for pictures.
    The ripped gun is the GAME'S model: keep rips and previews in the game folder, never in a repo.
Nothing here guesses the gun's shape beyond its bounding edges; the numbers it used are printed."""
import argparse, os

def read_obj(path):
    vs, lines = [], []
    for l in open(path, encoding="latin1"):
        lines.append(l)
        if l.startswith("v "):
            vs.append([float(t) for t in l.split()[1:]])
    return vs, lines

ap = argparse.ArgumentParser()
ap.add_argument("rips"); ap.add_argument("morph"); ap.add_argument("handle"); ap.add_argument("grip_z", type=float)
ap.add_argument("grip_y", type=float); ap.add_argument("out")
ap.add_argument("--overlap", type=float, default=0.03); ap.add_argument("--lift", type=float, default=0.02)
ap.add_argument("--skip-groups", default="", help="comma list of ripped OBJ group names to leave out (particles, ...)")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

gun_path = os.path.join(a.rips, a.morph, "gun.obj")
skip = set(g for g in a.skip_groups.split(",") if g)
gv, glines = read_obj(gun_path)
# only the vertices of groups we keep count for the edges
keep, cur, used = [], None, set()
gi = 0
for l in glines:
    if l.startswith(("o ", "g ")): cur = l.split(None, 1)[1].strip()
    elif l.startswith("v "):
        if cur not in skip: keep.append(gv[gi])
        gi += 1
gx = [v[0] for v in keep]; gy = [v[1] for v in keep]; gz = [v[2] for v in keep]
back_z = max(gz)
band = [v for v in keep if v[2] > back_z - 0.04]                 # the last 4 cm of the gun
rear_bottom = (sum(v[0] for v in band) / len(band), min(v[1] for v in band), back_z)

hv, hlines = read_obj(a.handle)
hz_min = min(v[2] for v in hv)
front = [v for v in hv if v[2] < hz_min + 0.05]                  # the first 5 cm of the handle's muzzle end
front_top = (0.0, max(v[1] for v in front), hz_min)

# move: the handle's front-top onto the gun's rear-bottom, then into the gun and up a little
t = (rear_bottom[0] - front_top[0], rear_bottom[1] - front_top[1] + a.lift, rear_bottom[2] - front_top[2] - a.overlap)
grip_cam = (0.0 + t[0], a.grip_y + t[1], a.grip_z + t[2])

def write_moved(src_lines, path, shift, header, drop=frozenset()):
    """drop: group names whose faces are left out (their vertices stay, so the numbering holds)"""
    with open(path, "w", encoding="latin1", newline="\n") as f:
        f.write(header)
        grp = None
        for l in src_lines:
            if l.startswith(("o ", "g ")):
                grp = l.split(None, 1)[1].strip()
            if grp in drop and l.startswith("f "):
                continue
            if l.startswith("v "):
                p = l.split()
                xyz = [float(p[1]) + shift[0], float(p[2]) + shift[1], float(p[3]) + shift[2]]
                f.write("v %.6f %.6f %.6f%s\n" % (xyz[0], xyz[1], xyz[2], (" " + " ".join(p[4:])) if len(p) > 4 else ""))
            elif not l.startswith(("mtllib", "usemtl")):
                f.write(l)

hdr = "# fit_handle.py: %s on %s; gun rear-bottom %.3f %.3f %.3f, handle front-top %.3f %.3f %.3f, overlap %.3f lift %.3f\n" % (
    os.path.basename(a.handle), a.morph, *rear_bottom, *front_top, a.overlap, a.lift)
# the handle about its grip (the add-on's file)
write_moved(hlines, os.path.join(a.out, "gun_handle_%s.obj" % a.morph),
            (t[0] - grip_cam[0], t[1] - grip_cam[1], t[2] - grip_cam[2]), hdr + "# origin = the pistol grip\n")
with open(os.path.join(a.out, "%s.gun_grip.txt" % a.morph), "w") as f:
    f.write("gun_grip = %.3f %.3f %.3f\n" % grip_cam)
# preview: gun + handle in the gun's frame (vertex numbers of the handle shifted after the gun's)
prev = os.path.join(a.out, "preview_%s.obj" % a.morph)
write_moved(glines, prev, (0, 0, 0), hdr, frozenset(skip))   # the left-out groups (HUD, crosshair) not drawn
nv = len(gv)
with open(prev, "a", encoding="latin1", newline="\n") as f:
    f.write("o handle\n")
    for l in hlines:
        if l.startswith("v "):
            p = l.split()
            f.write("v %.6f %.6f %.6f\n" % (float(p[1]) + t[0], float(p[2]) + t[1], float(p[3]) + t[2]))
    nn = sum(1 for l in glines if l.startswith("vn "))
    for l in hlines:
        if l.startswith("vn "): f.write(l)
    for l in hlines:
        if l.startswith("f "):
            out = []
            for c in l.split()[1:]:
                parts = c.split("/")
                parts[0] = str(int(parts[0]) + nv)
                if len(parts) == 3 and parts[2]: parts[2] = str(int(parts[2]) + nn)
                if len(parts) >= 2 and parts[1]: parts[1] = ""          # the handle has no UVs
                out.append("/".join(parts))
            f.write("f " + " ".join(out) + "\n")
print("%s: gun x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f; rear-bottom %s; gun_grip = %.3f %.3f %.3f" % (
    a.morph, min(gx), max(gx), min(gy), max(gy), min(gz), max(gz), tuple(round(c, 3) for c in rear_bottom), *grip_cam))
