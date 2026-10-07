# 2026-10-07 — Hard Reset in the OpenXR headset simulator

`[verified-live 2026-10-07, n=1]`, dev PC. Installed: `d3d9.dll` `ae49c7b1b487` (side-by-side capture + OpenXR
bridge, CPU handover), `nvapi.dll` `1921f0ddd086` (fake mode), 32-bit `openxr_loader.dll` `fb1e06de9653`,
`d3d9_openxr.txt`, `d3d9_sbs.txt`, `d3d9_vr.ini` → `openxr_simulator-32.json`.

- Session running at start-up; with `r_stereo_enable 1` the simulator shows both eyes of the live game at 60 headset
  frames/s (`headset-simulator.png`, from the OBS recording of the simulator window).
- **Eye order now correct** `[measured 2026-10-07]`: far scenery is 32 px further LEFT in the left half (was the
  opposite before the NVAPI eye-number fix), gun about 3 px the other way.
- **Cost**: the CPU handover reads back ~80 eye pictures/s, 13.6–14.8 ms each on average (max ~24 ms); about 40
  new frames/s reach the headset while it re-shows the last at 60/s. That is the next thing to speed up (or check on
  the home PC, where the dev PC's speed does not count).
- The game pauses itself when its window loses focus (clicking the simulator window).
- Not yet: the headset's own field of view, head tracking. The game's own FOV is shown.

**Faster hand-over, live** `[verified-live 2026-10-07, n=1]` (d3d9 `2fbd17857ae0`): WAIT (old) readback 11.5–13.9 ms
per Present, nearly all in LockRect (waiting for the copy); ASYNC (`d3d9_readback_async.txt`) **1.1 ms**, LockRect 0,
and every game frame handed over (49 of 49 at the dev PC's ~49 fps). Created by pool: MANAGED total 18 textures, so a
D3D9Ex shared-surface route would need those moved — not needed now (`faster-handover-log.txt`).
