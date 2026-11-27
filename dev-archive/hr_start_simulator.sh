#!/bin/bash
# Start Hard Reset (simulator), get through the intro and "Resume game", into play. Aim and HUD stay OFF (menus need
# that); controls on. Prints the first weapon line.
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
for try in 1 2 3 4; do
  python "$M" click "Hard Reset" 0.586,0.319 >/dev/null
  for i in $(seq 1 8); do sleep 3; tail -c 20000 "$L" | grep -aq "weapon: morph [0-9]" && break 2; done
done
sleep 5; $B in tap space >/dev/null; sleep 2
tail -c 20000 "$L" | grep -a "weapon: morph" | tail -1 | cut -c1-80
$B stats
