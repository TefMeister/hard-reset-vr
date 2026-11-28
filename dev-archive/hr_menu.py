"""hr_menu.py - from launch to "Resume game" pressed, without blind keys (2026-11-28).

Why: Enter presses timed for a game in front walked, with the game behind Tefa's windows (Backstage), through
New game -> New campaign -> a difficulty and started a new campaign, which wrote over the save (put back from the
backup). Escape on the main menu opens "Are you sure you want to quit the game?" (Escape again cancels). Matching
menu pictures failed: the panel is see-through over a moving scene and sways up and down.

What tells the screens apart is the add-on's own log: the intro logos draw about 360 things a second, the main menu's
3D scene 13,000-20,000. So:
  - wait, pressing nothing, until MENU_DRAWS is passed in MENU_LINES log seconds running;
    only if that has not happened after INTRO_WAIT_S: one Escape (the logos are up then, not the menu), and wait again;
  - then SETTLE_S, the window parked off the screen, Down, Enter (see the comment there; pictures 2026-11-28).
Exit 0 = Enter pressed; 2 = no menu found, nothing pressed after the last check."""
import os, re, subprocess, sys, time

CLI = os.path.expanduser("~/github-backups/mcp-game-bridge-cubed/tools/bridge_cli.py")
LOG = r"D:\SteamLibrary\steamapps\common\HardReset\d3d9_proxy_log.txt"
MENU_DRAWS = 5000
MENU_LINES = 3
INTRO_WAIT_S = 60
GIVE_UP_S = 150
SETTLE_S = 3
TRIES = 3
LOAD_CHECK_S = 5          # the log writes a line a second; MENU_LINES of them must show the load


def bridge(*words):
    return subprocess.run([sys.executable, CLI, "hardreset.exe", *words], capture_output=True, text=True)


def draws():
    try:
        tail = open(LOG, "rb").read()[-60000:].decode("latin1")
    except OSError:
        return []
    return [int(x) for x in re.findall(r"per s: present .*?draws to back buffer (\d+)", tail)][-MENU_LINES:]


start = time.time(); escaped = False
while time.time() - start < GIVE_UP_S:
    d = draws()
    if len(d) == MENU_LINES and min(d) > MENU_DRAWS:
        print("main menu (draws a second %s)" % d)
        time.sleep(SETTLE_S)
        # Off the screen first: behind Tefa's windows, Tefa's own mouse pointer passing over that part of the screen
        # hovers the menu and moves the selection (seen 2026-11-28: keys seemed to land anywhere). Parked past the
        # screen edge, a fresh menu has New game selected; Down = Resume game, Enter (pictures, 2026-11-28).
        bs = os.path.expanduser("~/github-backups/_lanes-next-wt/plugins/lanes/tools/backstage/backstage.py")
        pid = re.search(r'"hardreset.exe","(\d+)"', subprocess.run(["tasklist", "/FI", "IMAGENAME eq hardreset.exe",
                        "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout or "")
        if not pid:
            print("no game process"); sys.exit(2)
        subprocess.run([sys.executable, bs, "away", pid.group(1)], capture_output=True)
        time.sleep(1.5)
        # The menu may drop the first keys after it appears. So check the result: Resume game starts a load (the menu
        # scene stops being drawn); anything else leaves the menu scene up (New game's or Load game's panel), and one
        # Escape goes back to the main menu with New game selected, then Down, Enter again.
        for attempt in range(1, TRIES + 1):
            bridge("in", "tap", "down"); time.sleep(1.5)
            bridge("in", "tap", "enter")
            time.sleep(LOAD_CHECK_S)
            d = draws()
            if d and min(d) < MENU_DRAWS:
                print("off the screen; Down, Enter: loading started (try %d, draws %s)" % (attempt, d))
                sys.exit(0)
            print("try %d: the menu scene is still up (draws %s): Escape, again" % (attempt, d))
            bridge("in", "tap", "escape"); time.sleep(3)
        print("gave up after %d tries" % TRIES)
        sys.exit(2)
    if not escaped and time.time() - start > INTRO_WAIT_S and d and max(d) < 1000:
        print("still the logos after %d s (draws %s): one Escape" % (INTRO_WAIT_S, d))
        bridge("in", "tap", "escape"); escaped = True
    time.sleep(1)
print("gave up: no main menu in the log")
sys.exit(2)
