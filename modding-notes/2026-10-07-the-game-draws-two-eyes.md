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
