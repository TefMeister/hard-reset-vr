#!/bin/bash
# Quit Hard Reset by its own console and leave the add-on's switches as a headset player needs them (2026-11-28).
# Controls go off only for the typing (a mod turning controller presses into keys garbles console text); the bridge's
# "switch ... off" DELETES the switch file, so aim and controls are put back here after the game has gone: on
# 2026-11-28 they were left off and Tefa's next headset run had no buttons and a gun that would not turn.
g="/d/SteamLibrary/steamapps/common/HardReset"
B="python $HOME/github-backups/mcp-game-bridge-cubed/tools/bridge_cli.py hardreset.exe"
$B switch controls off >/dev/null 2>&1
$B console quit >/dev/null 2>&1
for i in $(seq 1 15); do sleep 2; tasklist | grep -qi hardreset || break; done
tasklist | grep -qi hardreset && { echo "STILL RUNNING: look before anything else (never force-kill)"; exit 1; }
touch "$g/d3d9_aim.txt" "$g/d3d9_controls.txt"
python "$HOME/github-backups/hard-reset-vr/dev-archive/set_runtime.py" vd >/dev/null 2>&1 && echo "runtime back on Virtual Desktop"
echo "closed; aim and controls ON"
