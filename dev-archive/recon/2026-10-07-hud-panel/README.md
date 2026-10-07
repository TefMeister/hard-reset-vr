# 2026-10-07 - the HUD on a flat panel at a set distance (`/pd`, dev PC, no game)

The game was NOT launched. Everything here ran without it: the maths test and a device test against the
OpenXR simulator, both through the shipped code (staging `hard-reset-vr/proxy-d3d9`, commit `972fcee`,
d3d9 `172eb78aa4ca`).

- `selftest-output.txt`: `hr_hud_math_test` (10/10) and `d3d9_hud_selftest` (13/13).
- `d3d9_log_hud_lines.txt`: the `hud` lines from the device test's log.

What the device test proves `[verified-numerically 2026-10-07, n=1 run]`: on a PURE device, a shader whose constant
table names `vHUDStereoParams` is recognised and a plain one is not; with `d3d9_hud.txt` the HUD square lands within
2 px of where a panel 2 m ahead belongs in each eye (expected 402.2 / 237.8 / y 147.5 / width 16.8 px from the lens
the simulator reported, measured 402.0 / 238.0 / 147.5 / 17), with crossed disparity once the lens shape is taken out;
the plain square never moves, so c0..c3 are given back after each HUD draw. The test shaders were compiled with HLSL's
default packing and were read as "by columns", which is what the game's own are expected to be `[hypothesis]` until
the first live log line says so.
