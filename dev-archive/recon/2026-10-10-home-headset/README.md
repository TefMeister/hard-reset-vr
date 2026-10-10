# 2026-10-10 home PC, real headset (Quest 3 via Virtual Desktop, sensor covered, nobody wearing it)

- Runtime: Virtual Desktop's 32-bit VDXR (d3d9_vr.ini runtime_json switched from SteamVR's steamxr_win32.json, which
  is kept commented). First launch on this PC: a UAC prompt from Steam's first-run install (Tefa clicked Yes), then a
  profile prompt (Ok), and the game went straight into New Game.
- `r_stereo_enable 1` in the console: every Present carries both eyes (eye calls L/R 108 per s), head lens ON +
  tracking ON, patched L 96 R 96 per s `[verified-live 2026-10-10, n=1]`.
- Rate: **~52 Presents/s with both eyes** (49-55), 41-49 of them handed to the headset, the rest "not ready"/dropped;
  the headset gets ~67-70 submits/s (repeats). The CPU readback costs **~13-17 ms per Present** (GetRenderTargetData
  ~6 + memcpy ~9) and is the likely cap `[measured 2026-10-10]`. The window did not freeze this time.
- Closed with console `quit`, clean. Video: MEGA Videos/hard-reset-vr/headset first look_2026-10-10_22-08-49.mp4.
- Still Tefa's: depth, comfort, scale.

## Flicker (Tefa wore it 22:20, "a lot of flickering, you can see that throughout the obs video")

- The video shows single frames (1/60 s, sometimes several) where BOTH eyes jump to the game's own camera view (the
  street ahead) instead of the head-tracked view, then snap back: 113 such jumps in 30 s of the 22:08 recording.
- The log matched: "render frames with pose 94 / without 29" per second in Tefa's run (~123 fps).
- Cause `[verified-live 2026-10-10, n=1]`: hr_head.c published_recently() computed `GetTickCount() - published` as
  unsigned, with `published = tick | 1`. In the same 16 ms tick as an even publish that is -1 = 0xFFFFFFFF, so the
  camera was refused and the frame drawn without the head. The faster the game runs, the more often.
- Fix: signed age (staging hard-reset-vr, build 52e783611121, installed; old f413b2778afe in _backup-2026-10-10).
  Re-measured at ~125 fps: "with pose 127 / without 0", "not published 0" three seconds running.
