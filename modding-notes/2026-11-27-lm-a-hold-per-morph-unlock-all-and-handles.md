# 2026-11-27 (/lm, Build PC, OpenXR Simulator): a hold per morph, every morph unlocked, Tefa's handles, a gun ripper

Tefa: "putting the cyborg hands into hard reset please, different poses for each morph on each weapon". During the
session: the guns "were not meant to be held in the flat game and have no clear triggers and such, handles"; two Meshy
handle models (grip, trigger, stock) sent to "blend in to the back of the gun"; "you are welcome to make the
transition point as you wish ... and change what you please"; and "let's see if you can even extract the weapons from
the game and make this work in blender, and put them back in the game too". Then Mad Max next.

## Done and seen live `[verified-live 2026-11-27]`

- **Which morph is in hand** (`hr_weapon.c`, the reader's): the add-on reads the game's script objects
  (`[0xADDEDC]` -> `q_World` -> player -> `qm_CurrentWeaponSlot` W1/W2 + weapon `qm_WeaponMode` 1..5) once a frame,
  cached. Live: "morph 0 (CLN assault rifle)", and an outside walk followed a gun switch both ways (n=1 each).
- **Every morph unlocked for testing**: writing `Active = 1` on the 28 `kin_*`/`el_*` upgrade flags makes all 10
  morphs selectable at once; the dial read SHOTGUN on key 2 and every morph's extra pieces showed in the pictures.
  Built in as the switch `d3d9_unlock_all.txt` (log: "unlock-all on PC ...: set 28 of 30"). Tefa's own saves (from
  2026-10-10) were copied first to `Documents\Hard Reset Extended\profiles-backup-2026-11-27-before-unlock`; nothing was
  saved in game this session, but compare the save files to the copy before the next play.
- **Pictures of all 10 morphs, side-on** (`dev-archive/recon/2026-11-27-morph-poses/all-10-morphs-sheet.png` and one
  file per morph). CLN changes the back block and barrel per mode; NRG keeps its orb and changes the rear coils and the
  lightning inside.
- **A hold per morph**: `d3d9_vr.ini [pose.cln1] .. [pose.nrg5]` (gun hand five curls, index on a full trigger, the
  other hand's five curls and its spot on the gun, `gun_grip`). First drafts for all ten are installed; the add-on
  logged "10 of 10 morph holds set" and switched to cln1 by itself. Bridge `pose cln3` / `pose auto` / `pose reload`.
  Blend 0.6 s (the CLN morph animation swaps parts at about 0.9).

## Built, not yet seen live

- **Handles**: Tefa's two models slimmed from 382k / 469k triangles to 6k each, 42 cm long, colours baked from their
  texture into the vertices (`dev-archive/blender/handle_from_glb.py`, outputs in
  `dev-archive/recon/2026-11-27-morph-poses/handles/`). The add-on reads OBJ vertex colours now and draws
  `gun_handle_<morph>.obj` / `gun_handle.obj` FIXED TO THE GUN at its grip point (so the handle stays on the gun while
  the aim catches up, and the gun mover puts the grip at the controller). Unit-tested (gun frame, colours); build
  `2b7060562865`.
- **Fitting script** `dev-archive/blender/fit_handle.py`: puts the handle's front-top on the ripped gun's rear-bottom
  edge, a little overlapped, and writes the handle centred on its pistol grip plus that morph's `gun_grip` line and a
  preview OBJ (gun + handle). Waiting for rips.
- **Gun ripper** (the reader's `hr_rip.c`): bridge `rip <label>` writes the held gun as `rips/<label>/gun.obj` in the
  game camera's frame (skinned on the CPU with the game's own bones), plus textures. Every vertex and index buffer in
  this game is DEFAULT-pool WRITEONLY, so it keeps CPU copies at Unlock when `d3d9_rip.txt` is present.

## What went wrong

- **The first ripper build hung the game at level load** (build `4d8e3145fc56`, `d3d9_rip.txt` present): presenting
  stopped the moment the load began, CPU near zero, memory frozen -> a deadlock between our buffer-copy lock and the
  loading thread `[measured, n=1]`. Log kept: `dev-archive/recon/2026-11-27-morph-poses/log-hang-tail.txt (the last 1,500 lines)`.
  The reader rewrote the copy hooks lock-free with no Direct3D calls (build `6e127f22e4e6`, a 4-thread stress test
  passes) and added a `nocopy` mode; not yet run.
- **The hung game could not be closed**: its own quit was impossible, a forced close left the process with 87 threads
  stuck inside Windows (most likely the graphics driver), still holding `d3d9.dll`, and Steam then refuses to start the
  game again. It needs a PC restart. Next run: restart first.
- Twice the console got stray letters ("quiwtf") because the controller buttons were on while typing; and one
  foreground attempt failed so keys went to the terminal window instead (nothing harmful was typed). The bridge's own
  `console` and keys are the safe route; check the game is in front before any real keystroke.

## NOT established

- Whether the per-morph holds LOOK right (drafts from pictures, nobody has judged them).
- Which way up the hand sits on a real controller (the old row), and the gun's grip vs our hand: the handles fix the
  gun side; the hand side is still the which-way-up row.
- Whether the lock-free ripper loads a level without hanging; whether Lock(READONLY) on these buffers returns real
  data (`nocopy`).

## Next, in order

1. Restart the PC (clears the stuck process). 2. Deploy `6e127f22e4e6` + current hands code, `d3d9_rip.txt` with
`nocopy`, load, `rip cln1`; then an empty `d3d9_rip.txt` and watch the load. 3. Rip all 10, run `fit_handle.py`
(handle A on CLN, B on NRG as a start), copy `gun_handle_<morph>.obj` and the `gun_grip` lines in, look in game,
pictures to Tefa.
