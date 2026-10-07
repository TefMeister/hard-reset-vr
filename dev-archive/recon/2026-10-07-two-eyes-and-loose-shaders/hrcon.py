"""con.py "<command>" [--keep] - open Hard Reset's console (Ctrl+~), type a command, Enter, close it."""
import ctypes, ctypes.wintypes as W, sys, time
u = ctypes.windll.user32

class KI(ctypes.Structure):
    _fields_ = [("wVk", W.WORD), ("wScan", W.WORD), ("dwFlags", W.DWORD), ("time", W.DWORD), ("dwExtraInfo", ctypes.c_size_t)]
class U(ctypes.Union):
    _fields_ = [("ki", KI), ("pad", ctypes.c_byte * 32)]
class INP(ctypes.Structure):
    _fields_ = [("type", W.DWORD), ("u", U)]

SC_CTRL, SC_GRAVE, SC_ENTER = 0x1D, 0x29, 0x1C
KEYUP, UNICODE, SCAN = 0x2, 0x4, 0x8

def send(sc, flags):
    i = INP(1); i.u.ki = KI(0, sc, flags, 0, 0)
    u.SendInput(1, ctypes.byref(i), ctypes.sizeof(INP))

def chord():
    send(SC_CTRL, SCAN); send(SC_GRAVE, SCAN); time.sleep(0.05)
    send(SC_GRAVE, SCAN | KEYUP); send(SC_CTRL, SCAN | KEYUP)

h = u.FindWindowW(None, "Hard Reset")
u.SetForegroundWindow(h); time.sleep(0.3)
chord(); time.sleep(0.5)
for ch in sys.argv[1]:
    send(ord(ch), UNICODE); send(ord(ch), UNICODE | KEYUP); time.sleep(0.02)
time.sleep(0.2)
send(SC_ENTER, SCAN); send(SC_ENTER, SCAN | KEYUP); time.sleep(0.4)
if "--keep" not in sys.argv:
    chord()
