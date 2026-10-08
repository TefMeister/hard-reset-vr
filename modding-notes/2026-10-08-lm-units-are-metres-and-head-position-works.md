# 2026-10-08 (dev PC, `/lm`, two launches, driven by Claude): one unit is a metre, and head position works

*Recorded: `units-per-metre_2026-10-08_15-38-03.mp4`, `head-position_2026-10-08_15-45-36.mp4`.
Pictures and log extract: `dev-archive/recon/2026-10-08-units-and-hud/`.*

## In plain words

One game unit is one metre. With that set, moving the (simulated) head sideways or forward now moves
the view the way a real head would, in the OpenXR simulator. The HUD-panel test runs but does not move
the health dial, because that dial is a 3D object on the gun, not a flat overlay.

## Measured

- **Up is z.** Walking changes x/y only; z stays at ~3.1-3.3 with a small step bob `[verified-live 2026-10-08, n=3 walks]`.
- **Walking speed:** forward 20.7 units in a 3 s hold and 35.6 in a 5 s hold, about 7 units/s; backwards
  20.4 in 5 s (slower backpedal, or a bump) `[verified-live 2026-10-08, n=3]`.
- **The game's own numbers** (reader, from the unpacked scripts `[inferred-static 2026-10-08]`): Speed 6.6,
  capsule height 2.0, radius 0.5, eye at 1.65 above the feet (`user.nut` CAMERA_POS), Jump 6.6, no crouch.
  Walking at ~7 against 6.6 and a 2.0 m capsule with eyes at 1.65: **units are metres**. `units_per_metre=1.0`.
- **Head position on** (`[xr] head_position=1`, `units_per_metre=1.0` in `d3d9_vr.ini`, read at start-up):
  the log shows the offset as sent; x=+0.15 moves the held gun LEFT in view and x=-0.15 moves it right;
  z=-0.3 moves the eye forward along the gun and past the dial; back to 0 restores the view exactly
  `[verified-live 2026-10-08, n=1 each]`. At x=+0.5 the gun and dial leave the view: correct for a
  body-fixed gun ~0.3-0.5 m from the eye. The reader checked the maths numerically: no bug
  `[verified-numerically 2026-10-08, n=1]`.

## HUD panel

`d3d9_hud.txt` on: `placed 60-70/s` (by columns), `not screen-space ~1300/s`; switching it off changed nothing
visible `[verified-live 2026-10-08, n=1]`. The health dial is a 3D model attached to the gun (it moves with
head parallax exactly like the gun), so the panel test cannot catch it. The ~1 placed draw per frame is
something small. Switch file left OFF (`d3d9_hud.off`).

## Driving notes

- `r_stereo_enable 1` must be typed each launch (not saved).
- The console command `quit` closes the game cleanly; easier than the in-game menu, which is drawn twice in
  side-by-side mode.
- Too many Enters at the intro open NEW GAME → New campaign (difficulty list next, which would start a new
  campaign). Back is safe; use about 4 Enters, then click Resume.
- The simulator preview window had been squashed to 1744x143; resized to 1300x620 for usable screenshots.
- The game pauses (pause menu) when it loses focus; Escape resumes.

## Not established

- Lighting/fog still use the game's own eye position (reader: c15/c51 not moved); minor at small offsets.
- Nobody has worn it; the home-PC headset run is still owed.
