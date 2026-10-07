# 2026-10-07 — Hard Reset draws two eyes, and takes our edited shaders

Dev PC, `/lm`, unattended (Tefa at work).

- **Edited shader files work**: a one-line test turned the whole game world red, the screen display untouched. We can
  change how the game draws without hooking into it.
- **The game draws both eyes** once its stereo setting is on: it tells our small helper file "left, right, left,
  right" about 120 times a second each.
- **But the window then freezes** on the last picture while the game carries on: the two eye pictures go somewhere we
  cannot see yet. The reader is building the piece that catches each eye's picture.
- Recorded with OBS (game window only).

Not established: where the eye pictures go; whether they really differ (no picture of either eye yet).

## Later the same day: both eyes side by side, with depth

- Our two small helper files now fool the game's stereo checks, catch each eye's picture and show both side by side
  in the window, at full speed, with the HUD in both.
- With a real eye distance, far-away things sit 32 pixels apart and the gun only 3: real depth.
- Not yet known: whether left and right are the right way round. That needs eyes (or the headset).

## Evening: in the virtual headset

- Hard Reset now runs in the virtual headset: both eyes, live, the right way round.
- The hand-over to the headset is slow-ish on this PC (about 40 new pictures a second); making it faster is next, and
  the real test is the home PC with the real headset.
