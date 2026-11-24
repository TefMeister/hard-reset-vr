# 2026-11-24 (/lm, Build PC, OpenXR Simulator): cyborg hands from Blender, with fingers that move

Tefa asked for "actual hands also made for the game, something cyborg and cyberpunk looking in Blender, with movable
fingers so we can have an idea where they will dock on the weapons". Done in one session, unattended.

## What was made

- **The hand, in Blender, separate parts on a finger rig** (`dev-archive/blender/cyborg_hand.py`, run headless:
  `blender -b -P cyborg_hand.py -- <out>`): 65 parts (palm core, back plate, glow strips, knuckle guard, wrist cuff,
  pistons; per finger segment a plate, a joint drum, a glow line, tip pads and caps), 16 bones (wrist + 5 fingers x 3),
  five named poses (open, relaxed, gun_grip, fist, point) kept in the .blend as actions. Gunmetal, carbon joints, cyan
  light lines, magenta fingertip caps. Pictures and every export in `dev-archive/recon/2026-11-24-cyborg-hand/`.
- **Finger rig in the add-on** (the reader's build, staging `ab51f88`, d3d9.dll `a826fad72160`): parts named
  `<finger>_<1..3>[_anything]` turn about `pivot` lines from `hand_left.pivots` (written by the Blender script);
  index follows the trigger, the other fingers and thumb the grip; a fixed hold on the gun hand; the hand gets its own
  depth surface so curled fingers hide what is behind them. The OBJ parser's heap overrun on quads without normals
  is fixed (found by the reader under AddressSanitizer).

## What was seen live `[verified-live 2026-11-24, n=1]`

- The game loaded the model: 5,876 triangles a hand, the right hand mirrored, "fingers MOVE: 53 parts name a finger
  segment, 15 pivots" for each hand; ~630 eye pictures a second with hands, own depth failed 0.
- Trigger 0 / grip 0: open hands; trigger 1 / grip 1: both fists, in both eyes (`in-game-fingers-open.png`,
  `in-game-fingers-fist.png`).
- **The dock gap:** with the gun mover on, the game's gun floats about 0.1-0.15 m above and ahead of the hand drawn at
  the same controller (`in-game-gun-floats-above-hand.png`; gun mover off for comparison:
  `in-game-gun-mover-off-flat-place.png`). Read from pictures, not measured.
- **The aim, raw mouse off, on this PC:** the camera reached the aim's target pitch (-17.2) through plain mouse
  messages; `s_mouse_raw_input "0"` survived a game exit in the profile config. This closes the board's raw-mouse row
  for the Build PC.

## NOT established

- **Which way up the hand should be.** The reader recalls the OpenXR grip frame as +X normal to the palm and -Z through
  the closed fist (thumb up when holding a controller), while our hands are modelled palm-down (fingers -Z, back +Y).
  In the simulator, with plain poses, the hands lie flat; whether that is right in a real hand is one look in the
  headset `[hypothesis]`. The rig handles either (`palm 1 0 0` for the spec frame).
- The finger curl seen live was only the free-hand curl (menus); the gun-hand hold was not seen with the gun in hand.
- Docking itself: the gun's own grip spot vs our hand's grip point is not measured; only the gap is seen.

## Small things found

- Main-menu clicks did not register while the controller aim was on (again); `switch aim off` over the bridge, click,
  `switch aim on` once in play. An administrator window in front (Task Manager) blocks every synthetic click.
- The game rewrites the window size from `r_fullscreen_modes`; set that to `"1280x720"` too.
- Steam asks for a Windows "Yes" on this PC at every Steam start of Hard Reset: its `directx` first-run mark is missing
  here (the dev PC got it on 2026-10-07). A one-click fix file was left on the Desktop for Tefa.

## Tefa's word

- 2026-11-24, after the pictures: "hands look cool!" The look stays as made; no changes asked for.
