"""aimpose.py <yaw_deg> <pitch_deg> [hand=1] - point the simulator's controller (relative to the head, right hand at
its default place), then print the next two 'aim per s' lines of the game's log"""
import json, math, os, sys, time
SIMDIR = os.path.join(os.environ["LOCALAPPDATA"], "OpenXR-Simulator")
LOG = r"D:\Program Files (x86)\Steam\steamapps\common\HardReset\d3d9_proxy_log.txt"
yaw, pitch = float(sys.argv[1]), float(sys.argv[2])
hand = int(sys.argv[3]) if len(sys.argv) > 3 else 1
x = 0.20 if hand == 1 else -0.20
cmd = dict(hand=hand, posX=x, posY=-0.30, posZ=-0.40, yaw=math.radians(yaw), pitch=math.radians(pitch), trigger=0.0, buttonA=False)
path = os.path.join(SIMDIR, "controller_pose_command.json")
with open(path + ".tmp", "w") as f: json.dump(cmd, f)
for _ in range(50):
    try: os.replace(path + ".tmp", path); break
    except PermissionError: time.sleep(0.01)
size0 = os.path.getsize(LOG)
time.sleep(2.3)
with open(LOG, "rb") as f:
    f.seek(size0)
    new = f.read().decode("utf-8", "replace").splitlines()
for l in new:
    if "aim per s" in l:
        i = l.find("mouse sent")
        print(l[:15], l[i:i + 30], "|", l[l.find("camera yaw"):][:200])
