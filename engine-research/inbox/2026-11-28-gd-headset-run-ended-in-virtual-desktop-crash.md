# Gold Digger, 2026-11-28 (full scan): the first headset look ended in a crash inside Virtual Desktop's runtime

From the shelves of the collector run `2026-11-28_01-34-41` (Tefa's first headset look at the Meshy gun frames,
graft build, Virtual Desktop):

- **The run ended in a crash in Virtual Desktop's 32-bit Oculus runtime, not in our code**: crash dump
  `PC1-2026-11-28_01-42-08-dedd4c` (crashes shelf): `0xC0000409 stack buffer overrun / fail-fast` in
  `VirtualDesktop.LibOVRRT32_1.dll+0x1EABC` `[measured 2026-11-28, n=1]`. The proxy log
  (`PC1-2026-11-28_01-42-08-826f5e`) runs normally up to 01:41:56 (morphs nrg1 -> nrg5 switched, hands and gun
  drawing every second); nothing of ours warns before it. The board's 2026-11-28 lines do not mention it.
  Unknown yet: whether the game was quitting at that moment (a crash on the way out) or still in play. Worth
  watching at the next headset run: if it comes back, test with the SteamVR / OpenXR route instead of the Oculus
  one to see whether it follows the runtime. `[hypothesis]`
- **Camera Jitter BeG0nE on the same run** (`PC1-2026-11-28_02-51-30-0fe2d6`): JITTER in 64 of 278 turning
  seconds; the camera sometimes holds still although the pose was fresh (the value written did not change), and
  85% of pictures carry the pose from BEFORE last, so the camera trails the head by one frame (a swim more than a
  jitter) `[measured 2026-11-28, n=1]`. Full report: `begone.py report camera-jitter latest`.
- **Ghost Hand on the same run** (`PC1-2026-11-28_02-51-30-755d47`): 38 of 38 front grabs and 25 of 25 stacked
  finished; the left hand trails its controller by 2 frames (27 ms), the right by 1 (13.5 ms) `[measured 2026-11-28, n=1]`.

Proposed board row (PD -> VR USER): "Hard Reset: the head pose reaches the camera one frame late (Camera Jitter
2026-11-28); find which step holds the older pose, then Tefa wears it", and a watch line for the Virtual
Desktop crash.
