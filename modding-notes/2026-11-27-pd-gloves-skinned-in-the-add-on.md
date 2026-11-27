# 2026-11-27 late (/pd, Build PC): Tefa's two gloves bent in the add-on, as Blender bends them

**The game was not launched and nothing here has run in it.** Everything below is compile-verified and checked
numerically against Blender; the look, the fit on the controller and the speed are for the next headset run.

## What was built

1. **An export from Blender** (`dev-archive/blender/glove_export.py`, run headless on `meshy_hand_<side>_skinned.blend`,
   never on the open Blender; the source files are not saved over). Per glove: slimmed, every point capped at 4
   bones, measured with Skin Checker in the grip, trigger-finger and fist poses beside the full glove, then written
   as `hand_<side>.hrsk` (points with normal, UV, 4 bones + weights; triangles; the 16 bones' rest frames and each
   bone's full-curl angle = Skin Checker's fist), `hand_<side>.tga` (the base colour, 1024 x 1024) and
   `hand_<side>_golden.bin` (Blender's own bent points for the grip and the fist, for the C test). The slimmed glove
   is also saved as `meshy_hand_<side>_game.blend` beside the source, for Tefa's eye.
2. **The add-on bends them** (staging `hard-reset-vr/proxy-d3d9/src/hr_hands_skin.c`, wired into `hr_hands.c`; the bend and lighting are done once a frame and reused for the second eye): a
   hand with a `.hrsk` beside the exe is drawn as that glove; each frame the rig's five finger curls (trigger, grip,
   the hold per gun morph, all as before) become joint angles (curl x the bone's full-curl angle), each bone's move is
   made into a dual quaternion, and every point is blended from its bones as dual quaternions, the signs lined up
   with the running sum in Blender's own bone order. Textured (modulated by the existing one-light shading), own depth
   on, the two hands separate models. `[hands] glove=0` turns it off; `glove_turn_deg` / `glove_offset_m` fit them.
3. **The grip point**: in the true OpenXR grip frame (see below), origin on the axis of the tube the four fingers
   wrap round in Skin Checker's grip pose.

## Measured

| | right glove | left glove |
| --- | --- | --- |
| full (from the session before) | 60,000 faces | 61,508 faces |
| slimmed to | **8,120 triangles** (7,885 points with UV seams) | **8,363 triangles** (8,769 points) |
| file | 0.51 MB + 3 MB texture | 0.56 MB + 3 MB texture |
| Skin Checker, grip: torn / thinnest joint / clipping | 0 / 0.91 / 93 (full: 0 / 0.90 / 260) | 0 / 0.96 / 142 (full: 0 / 0.96 / 317) |
| trigger finger | 0 / 0.90 / 17 | 0 / 0.96 / 96 |
| fist | 0 / 0.88 / 543 (full 0.88) | 0 / 0.93 / 351 (full 0.92) |
| our C bend vs Blender's, every point, grip and fist | worst **0.0002 mm** | worst **0.0002 mm** |
| a plain matrix blend would be off by up to | 19 mm (grip) / 41 mm (fist) | 4 mm / 9 mm |

`[verified-numerically 2026-11-27]` for the last two rows (`test/hr_hands_skin_test.c`, 47 checks, staging
`f8886c2`); Skin Checker rows `[measured 2026-11-27, n=1 per pose]`. 12,000 and 16,000 faces were also tried: no
better on any count (the right glove's thinnest joint went to 0.85-0.89), so the lightest was kept.

## Three traps found on the way (each cost one export)

- **Slimming lays long triangles across a joint** (18-54 torn edges at 8,000-20,000 faces). Fix: cut each edge whose
  two ends hang on different bones in two, copy the weights again from the full glove, repeat: one round brings it to
  0 at every size.
- **Copy weights from the STRAIGHT glove.** The files keep the glove bent into the grip, and Blender's weight copy
  reads the source as shown: the first try took every weight from the bent glove (thousands of tears).
- **Blender's Limit Total skipped points on the left glove** (points with up to 9 bones got through; the left mesh
  had the "paint only selected" mask on, and switching it off did not cure it). The cap is now done by the script,
  point by point. Before that, our bend was 1.6-2.1 mm off Blender's on 1,594 left points; after, 0.0002 mm.
- Skin Checker's thin-joint measure found no joints on the LEFT glove: its "cut discs" were all saved at one spot.
  The script then makes the joint planes from the rig (bone heads, square to the two bones' mean), which gives the
  numbers the session before reported by hand (grip 0.96, fist 0.92).

## The grip frame, and what is NOT established

The gloves are written in **OpenXR's grip frame as the spec words it** `[inferred-static]`: -Z through the tube the
fingers form, from the little finger towards the index; +X the palm's normal (away from the palm on the left hand,
into it on the right); +Y = Z x X, which here points to the wrist. That is **not** the frame the OBJ hands use (palm
down, fingers -Z), which the 2026-11-24 note already doubted; the gloves are the first hands drawn the spec's way.

The origin: each finger's posed joints (grip pose) fitted with a circle across the knuckle line, the four centres
averaged. Right glove: finger circles 39-59 mm radius, the spot sits 10 mm from the nearest glove surface in a
projection along the tube; left glove: 24-31 mm, but only 1 mm of room in that projection. A "roomiest spot" search
found 18-20 mm of room 12-25 mm away, but the left one ran to the edge of the search, so it was not used.
Pictures: `dev-archive/recon/2026-11-27-gloves-skinned/grip_<side>_slices.png` (with the export reports) (the glove's outline where each
finger wraps, the 35 mm ring a stand-in for the controller handle). **None of this says the glove sits right on a
real controller**: that is one look in the headset, then `glove_offset_m` / `glove_turn_deg`, no rebuild.

What would show the frame is wrong rather than a knob needing tuning: the glove turned a quarter turn about the
controller (palm facing up or down instead of towards the other hand while holding the controller upright): that is
the axes. Off by a few centimetres with the right turn: that is the offset knob.

Also not established: the speed (about 8,000 points a hand bent on the CPU once a frame, drawn once per eye; not
measured), the texture's look under the add-on's one-light shading (no normal
map: Meshy's other two textures are not used), and whether the curl angles (Skin Checker's fist = curl 1) look right
on the gun: the hold per morph (`[pose.*]`) is the knob.

## Files

- Blender side: `D:\claude video game stuff\blender\hard-reset-vr\meshy hands\game export\` (the four game files,
  goldens, reports, pictures) and `meshy_hand_<side>_game.blend`.
- Staging `f8886c2` (code only): `src/hr_hands_skin.{c,h}`, `hr_hands.c`, `test/hr_hands_skin_test.c`, `build.sh`
  (runs the golden check when `assets/gloves/` and `test/evidence/gloves/` hold the files), README, ini example.
  d3d9.dll **`eeec92e98437`** (staging `f8886c2` + the once-a-frame bend), not deployed (the game folder's crash state comes first, board row 1).
- ⚠️ The glove files themselves are NOT in git: the upload of the model and texture was refused by this session's
  safety check; they sit in the staging working copy (untracked) and in the Blender folder above, waiting for
  Tefa's word.
