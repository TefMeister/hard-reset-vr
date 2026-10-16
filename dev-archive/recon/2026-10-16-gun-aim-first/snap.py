"""snap.py <name> - ask the OpenXR Simulator for a picture of both eyes, save it as scratchpad/live/<name>.png (half size)"""
import json, os, sys, time
from PIL import Image
SIMDIR = os.path.join(os.environ["LOCALAPPDATA"], "OpenXR-Simulator")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "live")
os.makedirs(OUT, exist_ok=True)
outs = [os.path.join(SIMDIR, "screenshot." + e) for e in ("png", "bmp", "jpg", "jpeg")]
for o in outs:
    try: os.remove(o)
    except OSError: pass
t0 = time.time()
with open(os.path.join(SIMDIR, "screenshot_request.json"), "w") as f:
    json.dump({"timestamp": t0, "eye": "both", "include_ui": True, "requested_by": "snap"}, f)
while time.time() - t0 < 8:
    for o in outs:
        if os.path.exists(o) and os.path.getmtime(o) >= t0 - 0.5:
            time.sleep(0.3)
            im = Image.open(o).convert("RGB")
            im = im.resize((im.width // 2, im.height // 2))
            p = os.path.join(OUT, sys.argv[1] + ".png")
            im.save(p)
            print(p, im.size)
            sys.exit(0)
    time.sleep(0.1)
print("no picture within 8 s")
