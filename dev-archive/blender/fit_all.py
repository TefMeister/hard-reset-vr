"""Run fit_handle.py for all 10 morphs: handle A on CLN, B on NRG; leave out the HUD dial (left of the eye) and the
crosshair (right at the eye)."""
import os, subprocess, sys
RIPS = r"D:\SteamLibrary\steamapps\common\HardReset\rips"
OUT = os.path.join(RIPS, "fit")
REPO = os.path.expanduser("~/github-backups/hard-reset-vr/dev-archive")
FIT = os.path.join(REPO, "blender", "fit_handle.py")
H = os.path.join(REPO, "recon", "2026-11-27-morph-poses", "handles")
HANDLES = {"cln": (os.path.join(H, "handle_a.obj"), -0.27, -0.02), "nrg": (os.path.join(H, "handle_b.obj"), -0.25, -0.07)}
# NRG's back end is a cone whose middle is at about y -0.173: lift handle B so its receiver's middle meets it
EXTRA = {"cln": ["--lift", "0.10", "--overlap", "0.05"], "nrg": ["--lift", "0.08", "--overlap", "0.05"]}


def junk_groups(path):
    groups, cur = {}, None
    for l in open(path, encoding="latin1"):
        if l.startswith("g "):
            cur = l.split(None, 1)[1].strip()
        elif l.startswith("v "):
            groups.setdefault(cur, []).append([float(t) for t in l.split()[1:4]])
    return [g for g, vs in groups.items() if max(v[0] for v in vs) < 0 or max(v[2] for v in vs) > -0.1]


for m in ["cln1", "cln2", "cln3", "cln4", "cln5", "nrg1", "nrg2", "nrg3", "nrg4", "nrg5"]:
    h, gz, gy = HANDLES[m[:3]]
    skip = junk_groups(os.path.join(RIPS, m, "gun.obj"))
    r = subprocess.run([sys.executable, FIT, RIPS, m, h, str(gz), str(gy), OUT, "--skip-groups", ",".join(skip), *EXTRA[m[:3]]],
                       capture_output=True, text=True)
    print((r.stdout + r.stderr).strip(), "| skipped", len(skip))
