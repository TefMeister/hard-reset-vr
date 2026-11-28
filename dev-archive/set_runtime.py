"""python set_runtime.py sim|vd : which headset runtime line of d3d9_vr.ini is live (the other is commented)."""
import sys
p = r"D:\SteamLibrary\steamapps\common\HardReset\d3d9_vr.ini"
want = "OpenXR-Simulator" if sys.argv[1] == "sim" else "Virtual Desktop"
raw = open(p, "rb").read()
nl = b"\r\n" if b"\r\n" in raw else b"\n"
out = []
for l in raw.split(nl):
    s = l.lstrip(b";")
    if s.startswith(b"runtime_json=") and (b"OpenXR-Simulator" in s or b"Virtual Desktop" in s):
        l = s if want.encode() in s else b";" + s
    out.append(l)
open(p, "wb").write(nl.join(out))
print([l[:40] for l in out if b"runtime_json=" in l])
