# 2026-10-17 (live, dev PC, OpenXR Simulator): VR Bench plays the controllers, and every button works

Tefa handed the game over ("all yours"). The session launched it, drove it to play, and let VR Bench (the Lanes
plugin's robot player, with its OpenXR layer from `TefMeister/vr-bench`) move the head, the left hand and every
controller button in turn. Build installed: the 2026-10-16 controls build, unchanged; `d3d9_vr.ini` gained
`[controls] move=keys` (stamped `b37820f14446`).

## What it showed

- **Head:** the picture followed 5 of 5 moves (turn left, right, look up, tilt, lean) `[verified-live 2026-10-17, n=1]`.
- **Left hand:** our blocky hand moved the right way 3 of 4 times (left, up, right, down).
- **Buttons, read from the mod's own `controls per s` line** `[verified-live 2026-10-17, n=1]`: right trigger fire,
  left trigger alt fire, A jump, B switch gun, X weapon mode back, Y weapon mode on, menu the pause menu (a second
  press closes it), left stick forward W (keyboard walking), right stick sideways a 30° snap turn (the view turned).
- **The game never asks for a pad.** `the game asked the pad 0 times` in every second of two runs, so the virtual
  Xbox pad never reaches the game and stick walking did nothing. `move=keys` fixes walking for now.

## Found on the way

- **The aim stops the menus working.** With `d3d9_aim.txt` on, the main menu ignored every click: the aim loop
  sent the mouse 112 times a second and kept taking the cursor. Turned off, the first click worked. Start with the
  aim off and switch it on at play; the mod should stop steering while a menu is open (board row).
- **Simulator only: Space is also the right trigger.** Pressing Space on the keyboard alone made the mod fire, so a
  controller jump (the mod presses Space) also fired. VR Bench now holds every other input at rest during a button
  test, and A then pressed only jump.
- **Shots:** two more shots with the hand turned 25° left and right, at the ground down the street: no marks visible
  at that range. The question stays open; it needs a near wall.
- **Jitter (BeG0nE, automated):** the simulator's own smooth head sweep (±30°, 0.1 Hz) gave a usable recording with
  nobody turning a head. Pose fresh in 95-97% of frames; mid-swing read "smooth"; near the slow ends of the swing the
  camera held still in 22-39% of pictures `[measured 2026-10-17, n=1]`. To be repeated before anything is changed.
- **VR Bench itself was wrong at first:** its button check passed every button because this mod writes a log line
  every second. Fixed the same session (lanes plugin `0207d3b`): it now learns the log's usual lines first and
  reports the words that changed.

## Later the same day: the aim leaves menus alone

The mod needed no "menu is open" flag. It already reads where the camera points every frame, so it now notices when
the camera stops answering the mouse: after 10 frames of counts sent and no camera move it goes quiet, sending only a
3-count nudge every 30 frames, left and right in turn, and puts the pointer back where it was when the camera last
answered. When a nudge turns the camera again, steering comes back.

- First build (`3d3e11b6185d`, staging `df3687b`): main menu `quiet 120/s, mouse sent 0`, and a click worked
  `[verified-live 2026-10-17, n=1]`. But the 10 frames before it went quiet dragged the pointer to the left screen
  edge. On the comic "Press any key" pages a key press then minimised the game (with aim AND controls on; either
  alone did not), most likely a fire click landing outside the window `[inferred-static]`; and closing the pause menu
  overshot the turn to 42° for a 30° head turn before settling.
- Second build (`ab76b43a4113`, staging `5ec78dc`) puts the pointer back. Both switches on from launch: menus,
  comic pages and play all fine, the pointer stayed over the game, the pause menu read `quiet 60/s`, and closing it
  turned straight to −30.0° `[verified-live 2026-10-17, n=1]`. Leftover: in the pause menu the pointer sat ~100 px
  right of where it was put; still inside the game.

## Afternoon: walking, two hands, shots, jitter again

All with VR Bench setting the hands and the simulator setting the head.

- **Walking follows the head.** Head 45° left, both hands pointing straight ahead, stick forward: the mod turned the
  stick to −0.71 / 0.71 and pressed W and A together `[verified-live 2026-10-17, n=1]`. With the hand turned along
  with the head it pressed W alone, which is right too: the game's view already faces that way.
- **Two-handed holds.** Left hand apart: none. 30 cm ahead of the gun hand on its line: "front" (still "front" 8 cm
  off the line). 15 cm above the gun hand: "stacked". Apart again: none. The gun's aim stayed put throughout
  `[verified-live 2026-10-17, n=1]`.
- **Shots go where the hand points.** At a near wall with the head still: hand 15° left hit left of the middle,
  straight hit near the middle (a little right, where the gun sits), 15° right a little right, 25° right further
  right `[measured 2026-10-17, n=1]`. The holes were told apart by the order they appeared.
- **Jitter at the slow ends of a swing did not repeat.** A second smooth sweep read "smooth" in all 11 seconds, the
  slow ends holding the camera in 12-15% of pictures (22-39% the first time). The "JITTER" seconds in that log are
  all where VR Bench jumps the head in one go, which is not a real movement `[measured 2026-10-17, n=2]`.
- **Hazards found:** `vrbench.py learn` switches its layer off at the end (run `vrbench.py start` again before a
  hand-made test); with controls on, typing in the game's console picks up extra letters because the simulator
  turns some keys into controller presses and the mod then presses its own keys; the game opens its pause menu when
  it loses focus, and the aim correctly stays quiet there.

## Driving it

Launch to play, quitting, the music setting and the hazards are in the control profile
(`ai-game-control-profiles/routes/hard-reset/KNOWN.md`). Music muted: `s_sound_musicvolume "0"` in the profile's
`config.cfg` (backed up first).
