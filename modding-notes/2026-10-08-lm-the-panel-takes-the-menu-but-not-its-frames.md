# 2026-10-08 evening (dev PC, `/lm`, one launch, driven by Claude): the panel takes the menu, but not its frames

*Recorded: `hud-panel_2026-10-08_18-57-20.mp4`. Pictures and HUD log lines: `dev-archive/recon/2026-10-08-hud-panel-live/`.*

## In plain words

With the floating-screen test on, the pause menu's words and backgrounds do move onto a small panel that sits
where a screen 2 m ahead should be in each eye. But the menu's thin outline frames are not caught: they stay at
full size in their flat-screen place, the same spot in both eyes, so they would look wrong in a headset. Switching
the panel off puts the menu back to normal. The crosshair could not be judged at the simulator preview's size.

## Measured (d3d9 `172eb78aa4ca`, `d3d9_hud.txt` on, OpenXR simulator, stereo on)

- Gameplay: `hud per s: placed 544-592` (by columns), `not screen-space` ~1,700 (the 3D arm and gun screens,
  left alone as decided) `[verified-live 2026-10-08, n=1]`.
- Pause menu: `placed 2,100-2,160` `[verified-live 2026-10-08, n=1]`.
- Where things land in each eye (simulator preview, 640 px per eye; lens L -54/40, R -40/54 deg):
  far scenery sits 155 px further right in the left eye than in the right, matching the lens maths; the placed
  menu content (the small teal block) is centred at x 402 (left) and 237 (right), exactly the 402 / 238 the
  maths gives for a panel 2 m ahead `[measured 2026-10-08, n=1]`. Its size (~55 px, against ~72 px expected for
  the menu's share of a 50 deg panel) fits the whole screen being shrunk onto the panel.
- The menu's outline frames (box edges) sit at x 252-388 in BOTH eyes: the flat-screen position, not placed.
  For a real object that means the eyes would have to point outwards to fuse them `[measured 2026-10-08, n=1]`.
- Panel switched off live (menu still open): words, fills and frames all back in place, one consistent menu.

## Not established

- Which shader draws the frame lines (not one of the 34 the panel knows, or caught by the "not screen-space" test).
- The crosshair: present on screen, too small in the preview to measure.
- Whether the words are readable at that size on the panel (the whole 1280-wide screen shrinks to 50 deg).

## Next

Find the frame-line draws (static, from the shaders and the log), add them to the panel. Then look again,
with the simulator preview bigger or a per-eye capture at full size.

## Later the same session: lighting follows a leaning head (second launch)

The reader traced the eye position the lighting uses (c15 vertex, c51 pixel, and the light sorting) to the inverse
of the published view, which our head wrap has already moved, and fog uses depth and height only
`[inferred-static 2026-10-08]`. It built a log-only check (d3d9 `f413b2778afe`, staging `97a8202`; nothing written to
the game). Live, head centred: renderer eye = our eye = the game's own. Head leaned x = +0.3 m: renderer
(0.385, -0.883, 0.981) = our moved eye, the game's own stays at 0.085: **renderer - ours = 0.000 m**
`[verified-live 2026-10-08, n=1]`. So the "c15/c51 not moved" gap does not exist. Lines in
`dev-archive/recon/2026-10-08-hud-panel-live/lighting-eye-log-lines.txt`; recorded
`lighting-eye_2026-10-08_19-10-30.mp4`. The build stays installed (it only adds the log line). Shine is from the head
centre, not each eye (~3 cm off per eye), judged not visible `[hypothesis]`.
