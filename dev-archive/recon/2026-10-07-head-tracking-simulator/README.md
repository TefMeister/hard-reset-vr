# 2026-10-07 — headset lens and head tracking, in the OpenXR simulator

`[verified-live 2026-10-07, n=1]`, dev PC. d3d9 `f321323f9bbe` with `d3d9_headset_fov.txt` + `d3d9_head_track.txt`
(plus the async hand-over, side-by-side, OpenXR to `openxr_simulator-32.json`), nvapi `1921f0ddd086` fake mode.

- The camera hook wraps the game's camera (1 camera seen), patches both eyes and the culling view on every update
  (90/s at ~45 fps), every render frame carries its pose; nothing refused.
- Headset lens applied: L −54.0/40.0/44.0/−54.3°, R −40.0/54.0/44.0/−54.3°, IPD 64 mm (game fov was 65°).
- **Yaw 30 (head left)**: log shows yaw 30.0 applied; the window view swings left, the gun stays where the body faces
  (`window-y0.png` → `window-y30.png`).
- **Pitch 20, roll 15**: applied exactly; the window looks up and tilts (`window-ypr.png`), while **inside the
  headset the horizon stays level** (`headset-pitch20-roll15.jpg`) — the world stays put as the head moves.
- Not yet: head position (units per metre not measured), the HUD (still flat per eye), comfort in a real headset.
