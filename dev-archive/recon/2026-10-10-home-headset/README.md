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
