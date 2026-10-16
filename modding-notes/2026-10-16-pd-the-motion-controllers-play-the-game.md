# 2026-10-16 (no game running): the motion controllers play the game, with two hands on the gun — built, not yet run

Tefa: *"can you start wiring in the motion controllers as well?"*, then while it was being built: *"please keep in
mind it has to have two handing this gun"*. Same day as the hands and the controller-aimed gun (previous notes).

## What the game offers (static, `[inferred-static]` unless tagged)

- `hardreset.exe` imports **`XINPUT9_1_0.dll` → `XInputGetState`, `XInputSetState`** (IAT `0xA4105C`, `0xA41058`), and
  `RegisterRawInputDevices` / `GetRawInputData` / `GetAsyncKeyState` for mouse and keys.
- Pad settings exist but the pad's button layout is not stored anywhere readable: `s_pad_layout_buttons`,
  `s_pad_layout_sticks` (default / lefty / sticks / buttons), `s_pad_autoaim` (always / when firing / never) with
  radius and speed, look sensitivity, power and invert. Keys and mouse ARE: the player's
  `Documents\Hard Reset Extended\profiles\<profile>\binds.cfg` holds every binding (`+attack` left mouse, `+attack2`
  right mouse, `+jump` space, `toggle_weapon` F, `weapon_mode_prev/next` [ ] and the wheel, `arrow_toggle` R, `menu`
  Escape, `+sprint` left shift, W A S D, `select_weapon 1/2` Q E, `weapon_mode 1..9`, `menu_pda` P,
  `menu_objectives` O, `load_last` F9). There is no "use" key.
- The OpenXR simulator can be told only the controller pose, the trigger and A (`controller_pose_command.json`); it
  knows the Touch / Index / Vive / WMR / simple button paths, but nothing else can be pressed from a script.

## The design (`staging/hard-reset-vr/proxy-d3d9`, switch `d3d9_controls.txt`)

1. **Buttons read on the headset thread** (`src/hxr_buttons.c`): per hand trigger, grip, stick, stick click, plus
   A B X Y and menu, bound for Touch, Index, Vive, WMR and the simple controller IN THE SAME suggest call as the
   poses; a family that refuses the button paths is retried with the poses alone, so the hands can never be lost to it.
2. **Buttons press the game's own keys** (`src/hr_pad.c`, SendInput scan codes and mouse buttons, edge-triggered,
   all let go when the switch goes off or the game leaves the front): right trigger fire, left trigger alt fire,
   A jump, B switch gun, X / Y weapon mode back / on, right stick click the way arrow, menu the game menu, left stick
   click sprint (stays on while walking).
3. **Walking by a virtual Xbox pad:** the exe's `XInputGetState` import is pointed at ours, which reports pad 0
   connected with our left stick (a real pad still works and wins when pushed further). Analog: any speed and any
   direction. The stick is turned by (head yaw − game camera yaw), so stick forward walks where the HEAD looks while
   the gun points elsewhere (`move_relative=gun` for the gun's way). `move=keys` walks with W A S D instead.
4. **Snap turn** on the right stick (30°): the body frame turns about the world's up axis; the aim loop then turns
   the game camera after it by itself (the controller's target is fixed in the body frame).
5. **The body frame is now levelled** when locked: the world up axis is found as the axis the game camera's right
   side has no part of (the game never rolls the camera), and the camera's pitch of that moment is taken out, so the
   game's level ground matches the headset's level room. Before this a body locked while looking down stayed tilted.
6. **Two hands on the gun** (`src/hr_pad_math.c` `pm_two_hand`, used in `src/hr_aim.c`). Two holds count, from what
   BeG0nE Occlusion Drift learned on RE Village (worn and kept, 2026-10-02): the left hand **out in front on the
   barrel** (12–70 cm ahead along the gun, within 12 cm of its line), or **stacked just above the right hand** (3–35
   cm above, within 15 cm sideways), which keeps both controllers in the headset's sight so the aim never drifts.
   Letting go needs 1.5× the distance. By default the hand near the gun holds it by itself (`two_hand=button`: only
   with the left grip button). The gun aims where the RIGHT hand points (drift-free); `two_hand_aim=line` aims along
   right hand → left hand while held in front. What two hands change visibly comes with the gun at the hand (next):
   our left hand drawn on the fore-grip.
7. **The jitter log carries a line per controller read** (`jl_hand_q`, tracked or lost), which is what Occlusion
   Drift needs to show a controller lost behind the other.

**Which step runs last (PROTOCOL §11):** the keys and the pad stick are sent in the camera update of frame N and read
by the game at the start of frame N+1, the same one-frame path the mouse aim already proved live. The snap turn
changes the body frame applied to frame N+1's view.

## Proven without the game `[verified-numerically 2026-10-16, n=1]` (`test/hr_pad_math_test.c`, 21 checks)

Dead zone; stick forward with the head 90° left walks to the gun's left; snap fires once per push and re-arms at the
centre; trigger hysteresis; both holds taken, a hand 40 cm to the side not; the button mode; the let-go margin; the
default aim stays the right hand, the line mode aims along the hands only when held in front; a pitched camera in a
Y-up world levels to its yaw alone; a mirrored Z-up world is found too; a 30° snap turns LEFT in both. All older
self-tests still pass. Build `f91298f1b4e4` installed (backup `d3d9.dll.bak-2026-10-16-da3f75079a11`).

## Not known until the game runs

- Does the game read the pad every frame, and does it take a pad stick and the mouse **together**? If walking
  switches it into a pad mode that ignores the mouse, `[controls] move=keys`. `[hypothesis]`
- Pad aim-assist (`s_pad_autoaim`) may pull the aim once a pad is plugged in: set to never in the menu.
- Whether the shots leave along the gun (open since the first aim run).

## The first run

Game at gameplay with `d3d9_openxr.txt`, `d3d9_head_track.txt`, `d3d9_hands.txt`, the game window in front, then
`python test/sim_controls_drive.py record`: it switches aim and controls on and reports PASS / CHECK for the pad
hook, the game reading the pad, walking forward, the walk following a 60° head turn, a snap turn, both two-handed
holds, fire on the simulator's trigger, jump on its A, and switching the gun (B through the test file
`d3d9_controls_test.txt`, the stand-in for the buttons the simulator cannot press). Pictures per step in
`build/controls_run/`.
