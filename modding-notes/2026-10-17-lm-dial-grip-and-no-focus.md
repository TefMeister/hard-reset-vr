# 2026-10-17 evening (`/lm`, dev PC, simulator): the dial, the grip, and the game running in the background

Session: `/lm hard-reset-vr`, "all yours". The session launched and drove the game; VR Bench and the OpenXR
Simulator stood in for the headset; a background reader read the game's code and wrote two drafts.

## What works now

- **The gun's handle is in the hand.** The gun skeleton's root (where the handle is) was measured in the camera's
  frame and written into `d3d9_vr.ini` as `[gun] grip`. In the headset pictures the handle sits in the blocky
  right hand. `[verified-live 2026-10-17, n=1]` (judged by eye)
- **The dial shows its numbers and moves with the gun.** It used to turn into a black slab when the gun moved:
  near the eye the game draws it through a screen-effect pass that copies a patch of the screen chosen on the CPU.
  Switching that pass off (`r_animatix_pp_enable "0"` in the profile's `config.cfg`) makes the game draw the dial
  directly. `[verified-live 2026-10-17, n=1]` (pictures)
- **The game keeps running and takes our aim with another window in front.** Our d3d9 file hides the focus loss
  from the game (no pause) and posts the aim's mouse straight into the game's window. With a small window of ours
  in front, the camera turned to where the controller pointed. `[verified-live 2026-10-17, n=1]` This needed the
  game's plain mouse mode (`s_mouse_raw_input "0"`): in raw mode it ignored our posted mouse.

## Jitter report

18:51 report: JITTER 20 of 20 turning seconds, 78% of pose reads unchanged; frames cut from both recordings (game
window and simulator view), held-then-jump pictures on the sheets. The head was turned by 20 head commands a second
while the game drew 62 pictures a second, so most of it is likely the test's own steps `[hypothesis]`. Next: the
same sweep with the simulator's built-in pose sweep. OBS crashed once at the start of the second recording (NVENC
divide by zero on a 0x0 window); the new guard noticed, noted it in the report and restarted the recording. Lanes
0.77.0 now waits for the window to have a picture first.

## Closing the game

Posting `WM_CLOSE` to the window destroyed the window but left the game running with no window, so it had to be
force-closed `[verified-live 2026-10-17, n=1]`. Close with the console `quit` instead.

## Installed

`d3d9.dll c06ee1f6fcfa` (backup of the previous `a34fbca9eafe` beside it), `d3d9_vr.ini` with `[gun] grip`,
switches `d3d9_gun.txt`, `d3d9_aim.txt`, `d3d9_hands.txt` on, controls off. `config.cfg` gained
`r_animatix_pp_enable "0"`, `g_autopause_enabled "0"`, `s_mouse_raw_input "0"` (backup
`config.cfg.bak-2026-10-17-before-dial`). staging `a15d72e`.

## Next

The dial's place in the real headset (Tefa's eyes); the jitter sweep with the simulator's own smooth sweep; no-focus
keys with controls on.
