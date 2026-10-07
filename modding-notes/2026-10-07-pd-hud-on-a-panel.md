# 2026-10-07 - the HUD on a flat panel at a set distance (`/pd`, dev PC)

**The game was not launched, and nothing here has run in the game.**

## What the game does

Only three shaders do anything per eye: `font`, `font_out` and `animatix`. Each one computes
`clip = pos * mWorldToScreen` (VS `c0..c3`) and then adds `vHUDStereoParams.x` (VS `c29`) times a per-element factor
to `clip.x`. That is 3D Vision's HUD trick: the same flat screen in both eyes, nudged sideways a little. In a headset
it fills the lens edge to edge at no real depth, with the corners out of sight.

## What we do now (`d3d9_hud.txt`, off by default)

Our d3d9 stand-in recognises those shaders when they are created (their constant table names `vHUDStereoParams`).
The device is a PURE device (flags `0x454`), so nothing can be read back; we keep a copy of `c0..c3` and `c29` as the
game sets them. Before each draw with one of those shaders whose `c0..c3` is orthographic (a screen-space draw), we
upload `mWorldToScreen * A_eye` and zero `c29.x`; after the draw the game's own values go back.

`A_eye` is one 4x4: the HUD's screen point `(u, v)` becomes a point on a panel `D` metres ahead of the head
(`u * D * tan(width/2)`, height by the game's aspect), which is then projected into that eye with the headset's lens
and the eye's offset (the same `hm_eye_proj` the world uses). The panel's depth is pinned just above 0, so it is in
front of everything. Settings in `d3d9_vr.ini`: `hud_distance_m` (2.0), `hud_width_deg` (50).

A world-space `animatix` draw (a perspective `c0..c3`) is left alone, and counted.

## How well it is known

- The maths: `[verified-numerically 2026-10-07, n=10]` (ten checks) - both eyes triangulate to exactly 2 m, the screen
  edge sits at 25 degrees, the HUD stays on the same eye pixels when the head turns (head-locked), both register
  packings give exactly `pos * M * A`, and a planted wrong packing is told apart.
- The dll on a real device with the simulator: `[verified-numerically 2026-10-07, n=1]` (one run) (recon
  `2026-10-07-hud-panel`). Each eye's square within 2 px of an independent expectation.
- NOT established: that the game's HUD matrix really is orthographic and "by columns" (`[hypothesis]`; the log line
  `hud per s` says, live); that no other game draw uses these shaders in screen space (menus and the console use
  `font` too, and should float on the panel as well, which is wanted); whether 2 m and 50 degrees are comfortable
  (Tefa's eyes, later).

## The one look that settles it

Next flat run with the headset simulator (same switches as the head-tracking run), add `d3d9_hud.txt`:
- `hud per s: HUD draws placed N` with N > 0 and the HUD smaller and centred in the simulator window = working.
- `placed 0`, `not screen-space` high = the game's HUD matrix is not orthographic; the test needs widening.
- HUD in odd places or mirrored = the "by rows" case; the log says which packing it read.
