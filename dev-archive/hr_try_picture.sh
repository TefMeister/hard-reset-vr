#!/bin/bash
# One picture-size try on the simulator, behind Tefa's windows (2026-11-28):
#   hr_try_picture.sh <WxH> <texture quality> <tag> [anisotropy]   (r_texture_quality 0 = the highest, measured)
# writes r_fullscreen_modes and r_texture_quality into the profile's config.cfg (game closed), starts the game through
# hr_start_simulator.sh, stands still in play for 20 s, prints the eye size and the frame rates, takes a picture, quits
# through hr_stop.sh. Pictures: D:\Hard Reset GLB\work\shots\pic_<tag>.png (the game's model: never in a repo).
set -u
size="$1"; texq="$2"; tag="$3"; aniso="${4:-}"
D="$HOME/github-backups/hard-reset-vr/dev-archive"
g="/d/SteamLibrary/steamapps/common/HardReset"; L="$g/d3d9_proxy_log.txt"
C="$USERPROFILE/Documents/Hard Reset Extended/profiles/tefmeister/config.cfg"
B="python $HOME/github-backups/mcp-game-bridge-cubed/tools/bridge_cli.py hardreset.exe"
S="/d/Hard Reset GLB/work/shots"
tasklist | grep -qi hardreset && { echo "already running"; exit 1; }
python - "$C" "$size" "$texq" "$aniso" <<'EOF'
import sys, re
p, size, q, an = sys.argv[1:]
t = open(p, "rb").read().decode("latin1")
t = re.sub(r'(?m)^r_fullscreen_modes "[^"]*"', 'r_fullscreen_modes "%s"' % size, t)
t = re.sub(r'(?m)^r_texture_quality "[^"]*"', 'r_texture_quality "%s"' % q, t)
if an:
    if re.search(r'(?m)^r_anisotropy ', t):
        t = re.sub(r'(?m)^r_anisotropy "[^"]*"', 'r_anisotropy "%s"' % an, t)
    else:
        t = t.rstrip("\r\n") + '\r\nr_anisotropy "%s"\r\n' % an
open(p, "wb").write(t.encode("latin1"))
EOF
grep -a -E "^r_fullscreen_modes|^r_texture_quality|^r_anisotropy|^r_win_pos" "$C" | tr '\n' ' '; echo
python "$D/set_runtime.py" sim >/dev/null
bash "$D/hr_start_simulator.sh" 2>&1 | grep -E "menu|gave up|not in play|Resume" | tail -3
if ! tail -c 30000 "$L" | grep -aq "weapon: morph [0-9]"; then echo "NOT IN PLAY"; bash "$D/hr_stop.sh"; exit 2; fi
sleep 20
grep -a -E "CreateDevice|eye swapchains" "$L" | tail -2 | cut -c15-110
tail -c 200000 "$L" | grep -a "per s: present" | tail -10 | sed -E 's/.*present ([0-9]+).*/\1/' | sort -n | tr '\n' ' ' | sed 's/^/game frames a second (10 s, sorted): /'; echo
tail -c 200000 "$L" | grep -a "frames handed over" | tail -10 | sed -E 's/.*handed over ([0-9]+) of.*/\1/' | sort -n | tr '\n' ' ' | sed 's/^/headset frames a second: /'; echo
$B window | tail -1
$B shot "$S/pic_$tag.png" 1.0 | tail -1
bash "$D/hr_stop.sh"
