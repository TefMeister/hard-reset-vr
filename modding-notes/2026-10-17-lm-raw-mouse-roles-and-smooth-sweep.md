# 2026-10-17 late (`/lm`, dev PC, simulator): raw mouse fixed, the gun mover by shader role, the jitter was the test

Second `/lm` of the evening. The session drove the game; the reader worked from files in the background.

## Results

- **The 20-of-20 jitter was the test.** The same slow head turn done by the simulator itself (it renews the head
  every frame) gave JITTER in 2 of 35 seconds, both where the turn was switched on and off. My hand-made turn
  had sent only 20 head positions a second. `[verified-live 2026-10-17, n=1]`
- **Walking works in the background.** With a window of ours in front, the stick walked the player 13.5 m
  backwards in 3 s (forward did nothing visible: a wall was right ahead). `[verified-live 2026-10-17, n=1]`
- **Raw mouse works now.** The reader found the fault in our own code: one mouse message the game skipped (it
  ignores them in the console and menus) left a flag set, and nothing was sent again. Fixed; live, the game
  answered every message, in front and in the background. `[verified-live 2026-10-17, n=1]`
- **The gun mover only moves real gun parts.** Each shader is sorted at creation by what it reads (bones or an
  object matrix), and only matching uploads near the eye are moved. 1226 shaders known; the gun and the dial still
  follow the hand. `[verified-live 2026-10-17, n=1]`

## Installed

`d3d9.dll 39ec34a92f5d` (backup of `c06ee1f6fcfa` beside it). The game's raw mouse is back on (`s_mouse_raw_input 1`,
set in the console; the game saves it on quit).

## Reader

Two inbox notes (raw mouse, gun by role), folded into the dossier. Next job given: wire the Ghost Hand recorder.
