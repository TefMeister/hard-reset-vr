# 2026-10-07 — first light: both eyes side by side in the window

`[verified-live 2026-10-07, n=1]`, dev PC, windowed 1280x720. Installed: `nvapi.dll` `f9d665cc8b41` (fake mode:
SetDriverMode 0, IsEnabled 1, IsActivated -140 so the game never rewrites `r_stereo_enable`), `d3d9.dll`
`4fdd7e04b0b4` with `d3d9_sbs.txt`. Load in, then `r_stereo_enable 1` (the game resets it on device set-up).

- Eye count 2, SetActiveEye L/R ~120/s, both eyes captured 120/s, side-by-side composed 60/s, no failed Clears.
- `side-by-side.png`: two complete pictures, HUD in both.
- **The eyes are not yet apart**: best horizontal shift between the halves is 0 px for far scenery and for the gun
  `[measured 2026-10-07]`; our fake GetEyeSeparation/GetSeparation answer 0.0. Next: a real separation.

**With separation** `[verified-live 2026-10-07, n=1]` (nvapi `1921f0ddd086`: fake GetSeparation 50 %, GetEyeSeparation
0.1 → S 0.05, convergence 0.35, read back from the game's own settings): the halves now differ —
`side-by-side-with-separation.png`. Best horizontal match: far scenery **32 px**, the gun ~3 px (near the
convergence depth, as predicted) `[measured 2026-10-07]`. The far shift has the sign of crossed eyes in a parallel
left|right layout, so **the halves may be swapped** (eye 0 is RIGHT) `[hypothesis]` — check in the headset or swap.
