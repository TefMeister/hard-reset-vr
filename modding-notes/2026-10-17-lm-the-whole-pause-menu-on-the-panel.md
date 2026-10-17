# 2026-10-17 night (`/lm`, dev PC, simulator): the whole pause menu on the panel

The board's oldest HUD row, open since 2026-10-08: the menu's words and fills went onto the 2 m panel, its outline
frames did not.

## What was found

- **Which draw:** a census switch logged every flat 2D draw each second. One shader showed up only in the menu, drawing
  triangles and lines, left alone. `[verified-live 2026-10-17, n=1]`
- **Placing it was not enough.** With the extra switch on, the frames moved, but only a thin strip of them showed, at
  opposite edges in the two eyes.
- **Why:** the game cuts its menu list with a clipping box (scissor rectangle) set in flat-screen pixels. On the panel
  the menu sits elsewhere, so the box cut almost all of it away. The reader matched the strip's edges to the flat
  list's edges pixel for pixel.
- **Fix:** the clipping box now moves with the panel for each eye. Live: frames, buttons and words all show, the same
  in both eyes; switching the fix off empties the boxes again, which proves the cause. `[verified-live 2026-10-17, n=1]`

## Installed

`d3d9.dll 377990d19f6a`, with `d3d9_hud.txt` and `d3d9_hud_more.txt` on (the HUD panel is now on by default here).
Off switch for the clipping fix: `d3d9_hud_scissor.off`.

## Next

Check the crosshair and the gameplay HUD on the panel at full size.
