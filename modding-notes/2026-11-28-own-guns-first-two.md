# 2026-11-28 evening (Build PC, Fable, no game running): our own guns, the first two built and installed

Tefa: "let's see if this idea is actually doable, different guns instead of one morphing gun, try the first assault
rifle and shotgun please, and the hands, and if this works, we'll do the rest soon". Files: Meshy's textured GLB and
Meshy's part-split GLB of each gun, in `D:\Hard Reset GLB` (work folder `work` inside it; our own models, Meshy-made).

## Meshy's split copy has no paint: how the parts got it back `[measured 2026-11-28, n=2 guns]`

The part-split GLB has no UVs and no textures, is about 15.86 times smaller than the textured one and stands on z 0,
but its parts have the same shape. `dev-archive/blender/own_guns_split.py`: split parts laid over the textured model
by bounding box, the textured model slimmed to 20,000 faces with its UVs, each face given the nearest part, then
separated. Gap to the part: rifle median 2 mm, shotgun 5 mm (on a 1.9-unit model). Result: rifle 6 parts, shotgun 5,
each with the original colour / roughness-metal / normal maps (2048). Looked at in Blender: clean.

## Into the game: the whole gun through the graft, every game gun part hidden `[compile-verified: files built, NOT yet seen in game]`

`dev-archive/blender/build_own_guns.py`: each gun is put in its mode's rip frame with its muzzle tip on the game gun's
muzzle tip (so the muzzle flash should still start at the muzzle) and its barrel on the game gun's front centre, then
`graft_build.py --keep-uv --tex --hide <every gun group of that rip>` (all groups but the HUD dial and the crosshair).
No change to `hr_graft.c` was needed: a hidden anchor still triggers our draw (`h_dip` calls `after_draw` after a
fully hidden draw).

- rifle -> cln1: 0.80 m long, 20,000 triangles, 50 game parts hidden; shotgun -> cln2: 0.85 m, 20,000 triangles, 44 hidden.
- Game gun measured in the rips: 0.69 m from the back end to the muzzle, muzzle tip 0.853 m (cln1) / 0.847 m (cln2)
  ahead of the eye along the gun's own axis.
- Hand spots, estimated from the model's outline (not judged by eye yet):
  `[pose.cln1] gun_grip = 0.209 -0.312 -0.355`, `foregrip_ahead_m=0.328`, `foregrip_up_m=0.076`;
  `[pose.cln2] gun_grip = 0.222 -0.365 -0.325`, `foregrip_ahead_m=0.411`, `foregrip_up_m=0.049`.
- Installed in the game folder (game closed): `gun_graft_cln1.bin`, `gun_graft_cln2.bin`, the two `[pose]` sections
  of `d3d9_vr.ini`. What they replaced (yesterday's Meshy frame for cln1/cln2 and the ini) is kept in the game folder,
  `_backup-2026-11-28-before-own-guns`. cln3..cln5 and nrg1..nrg5 still hold yesterday's frames.

## NOT established

- Anything in the game: whether both guns show, sit right in the hand, how bright they are, whether the muzzle flash
  and tracers start at our muzzle, and what is lost with every game part hidden (the firing movement, the ammo dial
  parts on the gun, the mode's glow). One mistake caught before install: the hand spots were first written unscaled.
- The parts are joined into one rigid piece for this try; they are separate in the .blend for the moving parts later.

## 21:10-21:23, live on the OpenXR Simulator (Tefa's yes): both guns are in the game `[verified-live 2026-11-28, n=1, simulator]`

- Log: `gun_graft_cln1.bin` 21,458 vertices / 20,000 triangles, hides 50 game parts; `gun_graft_cln2.bin` 20,693 / 20,000,
  hides 44. In play on cln1: 280 anchor draws a second, 280 of ours drawn, 0 failed, 7,700 game part draws hidden a
  second; on cln2 the same with 6,720 hidden. 65 fps with the bridge taking pictures.
- Seen (pictures `dev-archive/recon/2026-11-28-own-guns-in-game/`): the rifle in mode 1 and the drum shotgun in mode 2,
  lit by the game, no game gun part left, the mode key swaps one whole gun for the other.
- NOT established: the muzzle flash (two pictures taken while Space was held show none; whether the shot fired is not
  known), brightness (the shotgun's wood reads near black: the colour is matched to the game part's dark average),
  size and feel in the headset, the hand spots (the simulator's stand-in hands hang wrist-up over the gun: the open
  "which way up" row, so the hold could not be judged).
- Mistakes of this run: the ini edit by sed left Virtual Desktop as the runtime (the first start sat at a flat main
  menu); then three mouse clicks aimed at "Resume game" opened "New game" and its lists (backed out with Escape, no
  campaign started, saves untouched). The arrow keys work: Down, Enter. `hr_start_simulator.sh` now uses them;
  `set_runtime.py sim|vd` (work folder) switches the runtime line. Left on Virtual Desktop for Tefa's headset look.

## 21:47-21:50, Tefa in the headset (Virtual Desktop) `[reported 2026-11-28, Tefa, n=1]`

Tefa: "size of the gun looked right! brightness was a bit too dark for guns and quite a bit too light for gloves.
gloves were too big, have to be taken down 30%. controller buttons didn't work, i could only move my hands around, and
the weapon but not rotate it, RT worked and the trigger finger curled. the graphics are really low in the headset. it
does look awesome though"; and "hands are visible through the gun" (the hands have no depth yet: the open DEPTH row).

- **Buttons and the gun's turn: my fault.** `d3d9_aim.txt` and `d3d9_controls.txt` were gone: the start helper's
  `switch aim off` (for the menus) and my `switch controls off` (before typing `quit`) delete the switch files, and
  nothing put them back. Log of Tefa's run: controllers ON, "keys/buttons posted 0" all through. Fixed: both files back;
  `hr_start_simulator.sh` switches aim on once in play; new `hr_stop.sh` quits and puts both back (and the runtime on
  Virtual Desktop, `set_runtime.py`).
- **Low picture**: each eye is the game's back buffer, 1280x720 (`xr: two 1280x720 eye swapchains`), stretched over
  about 94 x 99 degrees of lens: about 7 pixels a degree up and down. `r_texture_quality "0"` in config.cfg too, its
  meaning (low or high) not yet known; the game also has r_aa_quality, r_fxaa, r_anisotropy, r_shadows_quality,
  r_quality_lighting. Headset frames in play: 59-66 a second at this size. Not changed yet: needs a test run.
- Changed (game closed; the old files in the game folder's `_backup-2026-11-28-before-headset-fixes`): both guns
  rebuilt with `graft_build.py --bright 1.35`; gloves `[hands] scale=0.7`; glove textures darkened to 0.6
  (with a texture the add-on lights the glove white, so `colour=` does not tint it).

## 22:00-22:45, the picture size on the simulator, the game behind Tefa's windows (Backstage) `[measured 2026-11-28, n=1 each]`

Tefa: "yes, but on the background please, like re8 and the darkness do".

| eye size (= game window) | game frames a second in play | headset frames | readback ms per frame |
| --- | --- | --- | --- |
| 1280x720 | 60-69, median 63 | the same | 1.6 |
| 1920x1080 | 45-50, median 48 | the same | 3.5 |

- The graphics card (RTX 5080) was 40% busy at 1920x1080: the limit is not the card but our way of getting each eye
  to the headset (the copy back to the processor) and the game drawing every frame twice. That copy is the real job.
- `r_texture_quality "0"` is the HIGHEST (2 is plainly blurrier, pictures compared); it stays 0. It and
  `r_anisotropy` do not change live through the console, only at a start. `r_anisotropy "16"` is refused (the game
  wrote 0 back on quit); `4` is kept but shows no difference from the default, so the line was taken out again.
- Left for Tefa's headset look: `r_fullscreen_modes "1920x1080"` (config backed up first as
  `config.cfg.bak-2026-11-28-before-picture-size`); runtime on Virtual Desktop; aim and controls on.

## The menu behind Tefa's windows, and a new campaign started by mistake (my fault; put right)

- The old start helper's three blind Enters (timed for a game in front) ran, with the game behind other windows,
  through New game -> New campaign -> a difficulty and started a new campaign; it wrote over
  `save_16a5f693347862aa52b37dabb1c8c9b3.bin`. The game was quit before any checkpoint; the save was put back from
  `profiles-backup-2026-11-27-before-start-level` (fingerprint acc930ad..., the backup's); today's whole folder is kept
  beside it as `profiles-after-accidental-new-campaign-2026-11-28`. profile.bin left as the game wrote it.
- Learned: (1) Escape on the main menu opens "Are you sure you want to quit the game?" (Escape cancels it);
  (2) behind Tefa's windows, Tefa's own mouse pointer passing over that part of the screen hovers the game's menu and
  moves the selection, so keys seem to land anywhere; (3) the menu drops keys for its first seconds; (4) picture
  matching of the menu fails (see-through panel over a moving scene, the panel sways); the add-on's log tells the
  screens apart: intro logos about 360 draws a second, the main menu's scene 13,000-20,000, a load under 1,000.
- `hr_menu.py` now: nothing pressed until the log shows the menu; the window parked past the screen edge
  (`backstage.py away`); Down, Enter; if the menu scene is still drawn 5 s later, Escape and again (up to 3). Worked:
  try 1 dropped, try 2 loaded. `hr_stop.sh` brings the window back, quits, restores aim and controls, the window place
  (`r_win_pos` 603, 194) and the Virtual Desktop runtime. `hr_try_picture.sh <WxH> <texq> <tag> [aniso]` = one try.
