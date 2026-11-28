# 2026-11-28 late (Build PC, Opus, /pd, no game running): where Hard Reset's VR frames go

Tefa: "48 fps is not acceptable unfortunately, can you do work PD with no game running and see where this can be
stuck, because this is an old game and even in VR, should run very well."

## What the kept logs say `[measured 2026-11-27/28, the add-on's own counters, n = 14 runs]`

`dev-archive/perf_from_logs.py` over every kept run (`D:\Lanes Gold Digger\hard-reset-vr\logs`), seconds in play only:

| where / size | draws a frame (both eyes) | frames a second | ms a frame | eye copy ms |
| --- | --- | --- | --- | --- |
| 11-27 save spot (camera -1, 49, 10), 1280x720 | 3,600-3,700 | 82-94 | 10.6-12.2 | 1.6 |
| 11-28 save spot (camera -7, 103, 3, the street), 1280x720 | 6,000-6,100 | 62-69 | 14.5-16.1 | 1.6-1.8 |
| the same, 1920x1080 | 6,000 | 48-53 | 18.9-20.8 | 3.8 |

- The frame time follows the draw count: about 2.6-2.9 microseconds per draw call, whatever the spot. The RTX 5080
  was 40% busy at 1920x1080. **The game is limited by one processor core issuing draw calls**, and VR doubles them
  (the game's own stereo draws the whole scene once per eye: ~3,000 draws an eye on the street).
- On the same core, inside every frame, our add-on copied both eye pictures into the headset hand-over:
  1.6 ms at 1280x720, 3.8 ms at 1920x1080 (that is most of the 1280 -> 1920 loss besides the GPU work).
- Our per-call hooks are light: shader roles by hash table, HUD shaders a short list, the gun mover's matrix checks
  (~4,900 constant uploads and ~12,700 bone matrices a frame: well under a millisecond). The device's MULTITHREADED
  flag is the game's own (passed through), not ours. The ripper hooks nothing without `d3d9_rip.txt`.

## Built, compile-verified, installed SWITCHED OFF `[compile-verified 2026-11-28]`

1. **The eye copy on its own thread** (`d3d9_readback.c`): the game thread locks the landed memory surface and a copy
   thread does the memcpy + hand-over; the surface is unlocked at a later Present (waited for only if the ring comes
   round first). Log line says which, and counts waits and skips. `d3d9_vr.ini [xr] readback_copy_thread=1` turns it
   on (installed as 0). Expected: -1.6 ms a frame at 1280x720 (63 -> ~70 fps), -3.8 ms at 1920x1080 (48 -> ~58).
2. **DXVK under the add-on** (`d3d9_proxy.c`): with `d3d9_dxvk.txt` AND `d3d9_dxvk.dll` beside the exe, DXVK's D3D9
   (v3.2, 2026-11-26, x32 `d3d9.dll` renamed; sha256 6db168cd...) is loaded as the "real" d3d9 instead of Windows'
   own. DXVK does the driver work on its own thread, the usual cure for draw-call-bound DX9 games `[hypothesis]` for
   this game: the game's NVAPI stereo goes through our nvapi stand-in, not the driver, so it should not care.
   `d3d9_dxvk.dll` is in the game folder; the switch file is NOT.
- Game folder backup: `_backup-2026-11-28-before-copy-thread` (the old d3d9.dll and ini). Self-tests: 21 pass;
  `d3d9_hud_selftest` fails 4 HUD checks on the code from BEFORE this change too (a stale test, on FAULTS.md); it
  never reaches the headset copy, so it proves nothing about change 1.

## Game settings that can cut draws (names from the exe, untried)

`r_shadows` (0/1), `r_shadows_directional`, `r_shadows_point`, `r_shadows_spot`, `r_shadows_caster_cull_size`
(skip small shadow casters), `r_lights_min_size`, `r_offscreen_min_distance`, `r_draw_decals`, `r_particle_quality`.
Shadow maps are very probably drawn once per eye by the game's stereo; how many of the 6,000 draws they are is the
first thing to measure (`r_shadows 0` live through the console, then back).

## The next run (simulator, behind Tefa's windows), each step measured on the street spot

1. baseline; 2. `readback_copy_thread=1`; 3. + `d3d9_dxvk.txt`; 4. console `r_shadows 0` (only to measure the
share), then `r_shadows_caster_cull_size` up. Then the same at 1920x1080. The game is back on 1280x720 now.
