"""aimsweep.py [secs] - sweep the simulator's right controller round an oval (yaw +-25, pitch +-12, one lap per 5 s),
then report the game's aim error over the sweep from its log; 'shoot' fires one shot at 30 deg left afterwards"""
import ctypes, json, math, os, re, sys, time
SIMDIR = os.path.join(os.environ["LOCALAPPDATA"], "OpenXR-Simulator")
LOG = r"D:\Program Files (x86)\Steam\steamapps\common\HardReset\d3d9_proxy_log.txt"
PATH = os.path.join(SIMDIR, "controller_pose_command.json")

def send(yaw, pitch):
    cmd = dict(hand=1, posX=0.20, posY=-0.30, posZ=-0.40, yaw=math.radians(yaw), pitch=math.radians(pitch), trigger=0.0, buttonA=False)
    with open(PATH + ".tmp", "w") as f: json.dump(cmd, f)
    for _ in range(50):
        try: os.replace(PATH + ".tmp", PATH); return
        except PermissionError: time.sleep(0.005)

def game_in_front():
    u = ctypes.windll.user32; k = ctypes.windll.kernel32
    h = u.GetForegroundWindow(); pid = ctypes.c_ulong()
    u.GetWindowThreadProcessId(h, ctypes.byref(pid))
    hp = k.OpenProcess(0x1000, False, pid.value)
    buf = ctypes.create_unicode_buffer(512); n = ctypes.c_ulong(512)
    ok = k.QueryFullProcessImageNameW(hp, 0, buf, ctypes.byref(n)); k.CloseHandle(hp)
    return ok and buf.value.lower().endswith("hardreset.exe")

secs = float(next((a for a in sys.argv[1:] if a.replace('.', '').isdigit()), 12))
size0 = os.path.getsize(LOG)
t0 = time.time()
while time.time() - t0 < secs:
    a = 2 * math.pi * (time.time() - t0) / 5.0
    send(25 * math.cos(a), 12 * math.sin(a))
    time.sleep(1 / 30)
send(0, 0)
time.sleep(1.5)
with open(LOG, "rb") as f:
    f.seek(size0); new = f.read().decode("utf-8", "replace").splitlines()
errs = []
for l in new:
    m = re.search(r"aim per s.*?mouse sent (\d+).*?camera yaw ([-\d.]+) pitch ([-\d.]+), target yaw ([-\d.]+) pitch ([-\d.]+).*?error ([-\d.]+) / ([-\d.]+)", l)
    if m:
        errs.append((float(m.group(6)), float(m.group(7))))
        print(l[:15], "sent %s  camera %s/%s  target %s/%s  error %s/%s" % m.groups())
if errs:
    print("worst sampled error during the sweep: yaw %.1f, pitch %.1f deg (one sample a second)" % (max(abs(e[0]) for e in errs), max(abs(e[1]) for e in errs)))

if "shoot" in sys.argv:
    send(30, 0); time.sleep(1.0)
    if not game_in_front():
        print("SHOT SKIPPED: the game is not the window in front"); sys.exit(0)
    u = ctypes.windll.user32
    class MI(ctypes.Structure): _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("data", ctypes.c_ulong), ("flags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("extra", ctypes.c_void_p)]
    class INP(ctypes.Structure): _fields_ = [("type", ctypes.c_ulong), ("mi", MI), ("pad", ctypes.c_byte * 8)]
    for flags in (0x0002, 0x0004):   # left down, left up
        i = INP(0, MI(0, 0, 0, flags, 0, None)); u.SendInput(1, ctypes.byref(i), ctypes.sizeof(i))
        time.sleep(0.25)
    print("SHOT fired with the controller 30 deg left")
