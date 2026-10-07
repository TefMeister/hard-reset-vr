# 2026-10-07 — first light: both eyes side by side in the window

`[verified-live 2026-10-07, n=1]`, dev PC, windowed 1280x720. Installed: `nvapi.dll` `f9d665cc8b41` (fake mode:
SetDriverMode 0, IsEnabled 1, IsActivated -140 so the game never rewrites `r_stereo_enable`), `d3d9.dll`
`4fdd7e04b0b4` with `d3d9_sbs.txt`. Load in, then `r_stereo_enable 1` (the game resets it on device set-up).

- Eye count 2, SetActiveEye L/R ~120/s, both eyes captured 120/s, side-by-side composed 60/s, no failed Clears.
- `side-by-side.png`: two complete pictures, HUD in both.
- **The eyes are not yet apart**: best horizontal shift between the halves is 0 px for far scenery and for the gun
  `[measured 2026-10-07]`; our fake GetEyeSeparation/GetSeparation answer 0.0. Next: a real separation.
