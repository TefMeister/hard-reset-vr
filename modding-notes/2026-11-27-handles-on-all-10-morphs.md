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
