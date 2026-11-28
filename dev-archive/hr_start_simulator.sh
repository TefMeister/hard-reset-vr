#!/bin/bash
# Start Hard Reset (simulator), get through the intro and "Resume game", into play. Aim OFF for the menus and back ON
# once in play; HUD off; controls on. End a run with hr_stop.sh. M is no longer used for the menu. Prints the first weapon line.
g="/d/SteamLibrary/steamapps/common/HardReset"
B="python $HOME/github-backups/mcp-game-bridge-cubed/tools/bridge_cli.py hardreset.exe"
L="$g/d3d9_proxy_log.txt"
tasklist | grep -qi hardreset && { echo "already running"; exit 1; }
: > "$L"; : > "$g/d3d9_controls.txt"
# behind Tefa's windows from the first moment (Tefa 2026-11-28: "on the background please, like re8 and the darkness do"):
# Backstage starts it and hands the focus back; the add-on's focus keeper stops the pause, the bridge keys need no focus
BS="$HOME/github-backups/_lanes-next-wt/plugins/lanes/tools/backstage/backstage.py"
python "$BS" launch --watch hardreset.exe -- "$g/hardreset.exe" >/dev/null
sleep 8
$B switch aim off >/dev/null; $B switch hud off >/dev/null
# NO blind keys (2026-11-28: blind Enters behind Tefa's windows started a new campaign): hr_menu.py looks first
python "$HOME/github-backups/hard-reset-vr/dev-archive/hr_menu.py" || { echo "menu not reached"; exit 2; }
for i in $(seq 1 30); do sleep 3; tail -c 20000 "$L" | grep -aq "weapon: morph [0-9]" && break; done
tail -c 20000 "$L" | grep -aq "weapon: morph [0-9]" || { echo "not in play: look at the menu (bridge shot) before pressing anything"; exit 2; }
sleep 5; $B in tap space >/dev/null; sleep 2
$B switch aim on >/dev/null   # off only for the menus; Tefa 2026-11-28 got a gun that would not turn when it stayed off
tail -c 20000 "$L" | grep -a "weapon: morph" | tail -1 | cut -c1-80
$B stats
