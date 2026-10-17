# 2026-10-17 night (`/lm`, dev PC, simulator): Ghost Hand records the holds; the off hand on the fore-grip

Same `/lm` as the raw-mouse note. The reader built both in staging; the live session tested them.

## Results

- **Ghost Hand BeG0nE records Hard Reset's two-handed holds.** Each hold (stacked or front) is one gesture; the
  report read "stacked: 1 of 1 finished; front: 1 of 1 finished; the game's left hand trails the controller by 1
  frame (23 ms)". `[verified-live 2026-10-17, n=1]` The first wiring marked a frame ~13 times per picture (795 a
  second, 17.8 MB in 2 minutes); it now marks one per presented picture (60 a second).
- **The left hand goes onto the gun during a two-handed hold.** It is drawn 30 cm along the gun and 4 cm up from
  the grip, keeping its own rotation, and goes back to the controller when the hold ends. `[verified-live
  2026-10-17, n=1]` (pictures) The spot is a guess to tune by eye in the headset.

- **Smooth turn, as an option.** `turn=smooth` in `d3d9_vr.ini` turns the body continuously with the right stick,
  about 120° a second at full push, once per picture. Live: the view turned left at that rate. Snap stays the
  default, and the installed ini is back on snap. `[verified-live 2026-10-17, n=1]`

## Installed

`d3d9.dll 962b6f8f9ed2` (with smooth turn; backups of `60f57ec6112b` and `623ab36a6cb9` beside it). staging commit "Ghost Hand recorder (once per
picture), off hand on the gun's fore-grip".

## Also

The C Ghost Hand header went into the lanes plugin (`begone/ghost-hand/ghosthand.h`) for other native mods.
