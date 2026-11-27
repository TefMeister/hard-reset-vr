# 2026-11-27 afternoon (Build PC, OpenXR Simulator): all 10 guns ripped, Tefa's handles fitted and drawn in game

Tefa: "please work on getting those weapons done in Hard Reset - merge the existing weapons - all the morphs with the
stock, grip and triggers done with Meshy, let's see how that goes and if the weapon can be then put back so it still
works and animates like they do now."

**The shape chosen:** the game keeps drawing its own gun (every morph animation untouched); the add-on draws the Meshy
handle (stock, pistol grip, trigger guard) fixed to the gun's back, one fitted file per morph, and the gun mover puts
the handle's pistol grip at the controller. No game file is changed. Rebuilding the game's own packed models stays the
fallback if this looks wrong in the headset.

## Done and seen `[verified-live 2026-11-27, n=1, simulator]`

- **The lock-free ripper loads a level without hanging** in `nocopy` mode (build `6e0714f7f924`, `d3d9_rip.txt` =
  `nocopy`): Lock(READONLY) on the game's WRITEONLY buffers DOES return real vertex data. All 10 morphs ripped
  (`rips/<morph>/gun.obj` in the game folder, 17-22k triangles each, every file different). Each rip also catches the
  HUD dial (left of the eye) and the crosshair (at the eye); `fit_all.py` leaves out any group with max x < 0 or
  max z > -0.1.
- The bridge's key names have no `[` / `]`: `in tap 0xdd` (next mode) and `in tap 0xdb` (previous) work; `f` switches gun.
- **Fitted** (`dev-archive/blender/fit_all.py` -> `fit_handle.py`): handle A on CLN (grip at z -0.27, y -0.02 of the
  handle; `--lift 0.10 --overlap 0.05` so its stock line runs into the middle of CLN's back block), handle B on NRG
  (grip z -0.25, y -0.07; `--lift 0.08 --overlap 0.05` so its receiver meets the middle of NRG's back cone, about
  y -0.173). `fit_handle.py` now leaves the left-out groups out of the preview pictures too.
- **In game**: `gun_handle_cln1..nrg5.obj` beside the exe, and each `[pose.<morph>]` got its `gun_grip` line
  (`d3d9_vr.ini` backed up first as `d3d9_vr.ini.bak-2026-11-27-before-handles`). The log loaded all 10 handles;
  "handles drawn" counted while playing; switching CLN -> NRG -> next mode swapped the handle by itself. Pictures
  `dev-archive/recon/2026-11-27-handles-in-game/`: the CLN block sits ahead of handle A, the NRG orb right ahead of
  handle B.

gun_grip lines installed: cln1 0.225 -0.286 -0.102 · cln2 0.225 -0.285 -0.102 · cln3 0.226 -0.286 -0.102 ·
cln4 0.225 -0.356 -0.107 · cln5 0.225 -0.286 -0.106 · nrg1 0.272 -0.295 -0.135 · nrg2 0.271 -0.298 -0.107 ·
nrg3 0.271 -0.291 -0.132 · nrg4 0.269 -0.296 -0.138 · nrg5 0.270 -0.295 -0.133.

## NOT established

- How it looks and feels in the headset: the simulator's stand-in controllers move with the head, so no side view was
  possible; the level is dark (pictures brightened). The guns now sit further out from the hand (grip 10-14 cm behind
  the game's grip point), so the full length reads big: Tefa judges.
- The handles are drawn in flat grey vertex colours (Meshy's colours were baked in, but read light grey here).
- Whether the per-morph finger holds (drafts) still suit the new grip.

## Next

Tefa in the headset (runtime_json in `d3d9_vr.ini` points at the simulator: comment it out for Virtual Desktop), a
look at all 10 morphs; then adjust lift/overlap per morph in `fit_all.py` and rerun (game closed; handles load at start).

## Correction, same afternoon (Tefa, from the sheet of all 10)

Tefa: "the gun stocks are swapped on the weapons, the one that is on the energy gun is for the bullet gun". Now
**handle B (the receiver with the AR stock) on CLN** (grip z -0.25 y -0.07, `--lift 0.15`: its receiver's middle on
the middle of CLN's back block) and **handle A (the skeleton stock) on NRG** (grip z -0.27 y -0.02, `--lift 0.06`: its
top bar on the middle of NRG's back cone); overlap 0.05 both. Installed (game closed), not yet looked at in game.
gun_grip now: cln1-3 0.225 -0.329 -0.082 · cln4 0.225 -0.399 -0.087 · cln5 0.225 -0.329 -0.086 ·
nrg1 0.272 -0.222 -0.155 · nrg2 0.271 -0.225 -0.127 · nrg3 0.271 -0.218 -0.152 · nrg4 0.269 -0.223 -0.158 ·
nrg5 0.270 -0.222 -0.153. The pictures in `dev-archive/recon/2026-11-27-handles-in-game/` show the OLD pairing.

## Evening (Fable): the handle drawn THROUGH THE GAME'S RENDERER ("graft"), lit like the gun `[verified-live 2026-11-27, n=1, simulator, nrg1 only]`

Tefa, on the lowered NRG stock (handle moved 10 cm down, 9.5 cm forward: "this is getting better now!"): it "has to be
'melted' into the gun model with same sort of look and lighting and reflection and all that".

- **Why the old handle could not**: hr_hands.c paints it on the finished picture in a flat colour. **New: `hr_graft.c`**
  (switch `d3d9_graft.txt`, files `gun_graft_<morph>.bin`): right after the game draws one chosen gun part (the anchor,
  found by its index range), the same draw is repeated with our vertex and index buffer; shaders, textures, bones and
  states are the game's. Live on nrg1: 340 anchor draws a second, 340 handles drawn, 0 failures, 84 fps; the handle
  shows in the gun's worn grey metal with the scene's light and highlights
  (`dev-archive/recon/2026-11-27-handles-in-game/nrg1-handle-grafted-lit-by-the-game.png`, brightened).
- **The game's skinned vertex** (32 bytes): FLOAT16_4 position, UBYTE4N tangent, binormal, normal, FLOAT16_2 uv,
  D3DCOLOR weights, UBYTE4 bone indices. `tools/graft_build.py` (staging, proxy-d3d9) puts a fitted handle into the gun
  model's space on the anchor's bone: model -> camera map fitted from the rip itself, residual 0.00001 m on nrg1
  (anchor = the back cone, index 48135 x 1164 triangles, all 961 vertices on bone 32) `[verified-numerically]`.
- **How the game draws the gun** (from the rips): a depth/normal pass and a colour pass per eye. NRG's cone and lower
  arm are single draws in both passes; most CLN parts are single draws in the colour pass but BATCHED in the first pass
  (one draw whose index range contains several parts): graft_build.py writes every containing draw as an anchor too.
  CLN not yet tried.
- **Fault made and fixed the same hour**: asking weapon_morph() on every draw took the game to 2 fps; now only on a
  draw whose index range matches a graft (build `157eedb0a98a`).
- A side view in the simulator: aim OFF, then the head turned (yaw -75, pitch -20): the gun keeps the body's forward
  and crosses the picture.
- nrg1 `gun_grip` is now 0.272 -0.322 -0.250 (the lowered stock). Stand-in UVs: a strip of bare metal from the gun's
  texture (u 0.150..0.180, v 0.42..0.76).

Still to do: the other 9 morphs' graft files; the join remodelled and the handle unwrapped onto the gun's texture
(Blender, together with Tefa); the hand's pose on the new grip.

## Later the same evening: the graft on all 10 morphs `[verified-live 2026-11-27, n=1, simulator]`

Tefa: "that looks really cool! can you do the same with the bullet gun and then give me the glb files, I'll let Meshy
go over these and then we can go from there".
- CLN anchor = the lower body, index 45663 x 182 triangles (143 vertices, all on bone 2, residual 0), plus the batched
  first-pass draw that contains it (45201 x 3480); the same in all five CLN morphs. Stand-in UVs: the dark scratched
  plate of the CLN texture (u 0.73..0.86, v 0.64..0.76). NRG anchor 48135 x 1164 is in all five NRG morphs.
- Live: every morph cln1..nrg5 showed 320-344 handles drawn a second, 0 failed, 80 fps. nrg2..nrg5 gun_grip lowered
  like nrg1 (y -0.10, z -0.095).
- GLBs for Meshy (gun parts joined, HUD dial and crosshair left out, handle a second object), made by
  `dev-archive/blender/export_glb.py`; they hold the game's model, so they stay on the PC (work folder
  blender/hard-reset-vr/glb for Meshy), never in a repo. A few gun parts are untextured in them (draws with no
  colour texture in the rip: the glass and glow parts).
- What comes back from Meshy needs: the handle as its own part again (only OUR part can go into the game), its UVs on
  the gun's texture or its own texture (then hr_graft.c must swap the texture stages too: not built).

## The base frame of each gun, for Meshy (Opus)

Tefa: "can you just give me the base gun model without the morphing parts? so we can model the base frame and all the
moving parts will be added to that?"
- Every gun part is its own draw on its own bone (`part_bones.py`). Each mode's copy lined up on the handle's anchor
  part, then every part measured against mode 1 `[measured 2026-11-27, n=1 per mode]`:
  **CLN: 28 of 50 parts stay within 1 mm in all five modes** (the body, the lower block, the rails): the base frame.
  **NRG: only the back cone is rigid**; the lower arm, its front ring and the knuckles move up to 3.5 cm, everything
  else 13-27 cm (the orb cage, the coils): base frame = parts within 4 cm, in mode 1's pose.
- `export_base.py` (base list from `base_parts.py`-style measuring, kept as base_groups.json in the work folder) writes per
  gun: base frame alone, base frame + our handle (separate object), and mode 1's moving parts, all with one shared
  shift so they still fit together. Work folder `blender/hard-reset-vr/glb for Meshy/base frames` (the game's model:
  never in a repo). The CLN frame carries a flat textured card at its front (one of the fixed parts).

## Night: Meshy's whole bullet-gun frame in the game, the game's frame hidden `[verified-live 2026-11-27, n=1, simulator]`

Tefa sent a Meshy model made from our base frame + handle ("please add wires, low-tech connectors"): 660,824 faces,
one solid mesh, about 2.09x the game's size, own colour / roughness-metal / normal maps (2048).
- `meshy_fit.py` (Blender, numpy ICP with scale over 8 orientations): matched onto our base frame + handle, median gap
  13-16 mm. `meshy_slim.py`: decimated to 16,000 faces (the paint carries the detail; picture checked), written in
  the cln1 rip's camera frame with its UVs, plus its three textures.
- `graft_build.py` now: `--keep-uv` (its own UVs, tangents from them), `--hide @base_groups.json:cln` (the 28 fixed
  CLN parts it replaces), `--tex` (Meshy's maps -> the game's s0 colour, s2 specular+gloss, s4 normal with green
  flipped to DirectX, s6; brightness matched to the texels of ALL replaced parts: matching to the anchor part alone
  came out near black), written as "HRG2".
- `hr_graft.c` (build `2b6b7e7df9aa`): reads HRG2; a draw of the held gun's index buffer that covers a hidden part is
  drawn in the pieces around it (the batched first-pass draws), a wholly hidden part not at all; our textures set for
  our draw only, the game's put back. Live: 28 parts hidden (about 4,700 hidden part draws and 480 cut draws a
  second), the frame drawn 328-336 times a second, 85 fps; the game's moving top bar and barrel sit on Meshy's frame.
  Pictures `dev-archive/recon/2026-11-27-handles-in-game/cln-meshy-frame-in-game-*.png` (taken at r_gamma 2.2, put
  back to the default after).
- Learned the hard way: `start_level <name>` from the MAIN MENU crashes the game ("internal application error"; it
  then exits by itself; saves untouched, backed up first to profiles-backup-2026-11-27-before-start-level). The
  levels in data_10_levels.bin: level2, level11, low3, low3b, low4, mid1, mid3. The main menu panel sits at x 0.586 of
  the window (not 0.497); "Resume game" y 0.319.
- Not checked: the hand on Meshy's grip (gun_grip still handle B's), the normal map's direction, the other 4 CLN modes
  in the game (same file), how it looks in the headset.

## The energy gun's Meshy frame (installed, NOT yet seen in the game)

Tefa's second Meshy file (695,020 faces, 2.22x size) fitted onto our NRG base frame + handle A (median gap 8.5-12.8 mm),
slimmed to 15,999 faces, grafted on the cone (48135 x 1164, bone 32), hiding the 6 NRG frame parts (the cone and the
lower arm pieces 74292, 29115, 28275, 27579, 25251). Same file for nrg1..nrg5. Known limit: the game's arm pieces move
up to 3.5 cm between modes, ours stays in mode 1's place, so the game's knuckles and ring may sit a little off it in
modes 2-5. Its s6 came out a faint blue glow average (NRG's s6 is the glow map). d3d9_vr.ini now points at Virtual
Desktop (runtime_json) for Tefa's headset look at both guns; the simulator line is kept, commented.

## Close of the day: pictures, and where things stand

- Tefa on the Blender picture set: "some parts look bent" and "guns are too bright". Both were the pictures: the rip
  holds the gun as the game does (turned about 9.6 degrees toward the crosshair, tipped 3.9 degrees up: model x/y/z in
  the camera frame from the cln1 anchor fit), and a 50 mm camera close up bends a long gun. `photo_set.py` now turns
  the gun onto its own axes (model x right, y muzzle, z up), shoots the four flat views orthographic, and darkens
  Meshy's colour by the game file's scale (0.71) under dimmer light. The game's batched first-pass draws (no colour
  texture) are left out of pictures: they showed as white plates and never show in the game.
- d3d9_vr.ini runtime_json = Virtual Desktop (the simulator line kept, commented) for Tefa's headset look.
- **Next:** Tefa in the headset: both Meshy frames, all 10 modes, brightness at the normal r_gamma, the hand on
  Meshy's grips; then tune brightness (graft_build's s0 scale) / grip points per what is seen.
- Helper: `dev-archive/hr_start_simulator.sh` (start, intro, Resume game at x 0.586 y 0.319, into play) and
  `dev-archive/shot_zoom.py`.
