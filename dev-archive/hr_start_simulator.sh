#!/bin/bash
# Start Hard Reset (simulator), get through the intro and "Resume game", into play. Aim OFF for the menus and back ON
# once in play; HUD off; controls on. End a run with hr_stop.sh. M is no longer used for the menu. Prints the first weapon line.
g="/d/SteamLibrary/steamapps/common/HardReset"
B="python $HOME/github-backups/mcp-game-bridge-cubed/tools/bridge_cli.py hardreset.exe"
M="$HOME/github-backups/_lanes-next-wt/plugins/lanes/tools/menu-o-matic/menu_o_matic.py"
L="$g/d3d9_proxy_log.txt"
tasklist | grep -qi hardreset && { echo "already running"; exit 1; }
: > "$L"; : > "$g/d3d9_controls.txt"
cd "$g" && (cmd //c start "" hardreset.exe)
sleep 8
$B switch aim off >/dev/null; $B switch hud off >/dev/null
for i in 1 2 3; do $B in tap enter >/dev/null; sleep 3; done
sleep 3
# Resume game by the keys (2026-11-28): on the simulator the mouse click landed on "New game" whatever row was aimed at;
# Down once highlighted "Resume game" and Enter took it (seen once, after backing out of New game; from a fresh menu
# not yet checked). One try only: a second Down + Enter
# would walk into another row.
$B in tap down >/dev/null; sleep 1; $B in tap enter >/dev/null
for i in $(seq 1 30); do sleep 3; tail -c 20000 "$L" | grep -aq "weapon: morph [0-9]" && break; done
tail -c 20000 "$L" | grep -aq "weapon: morph [0-9]" || { echo "not in play: look at the menu (bridge shot) before pressing anything"; exit 2; }
sleep 5; $B in tap space >/dev/null; sleep 2
$B switch aim on >/dev/null   # off only for the menus; Tefa 2026-11-28 got a gun that would not turn when it stayed off
tail -c 20000 "$L" | grep -a "weapon: morph" | tail -1 | cut -c1-80
$B stats
