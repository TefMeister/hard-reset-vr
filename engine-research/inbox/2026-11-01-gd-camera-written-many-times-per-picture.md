# Gold Digger 2026-11-01: the jitter recorder's camera-write call fires 2 to 170 times per picture

From: `/gd` (inside `/fullscan`), the 2026-10-30 01:24 Camera Jitter report, compared with the 25 older Hard Reset
reports in BeG0nE's data.

Camera writes per second against pictures per second: 117-892 at ~60 pictures (10-17), 416-1,360 (10-23), and
**12,203 at 71.2 pictures on 10-30** (about 170 per picture) `[measured 2026-10-17..30, n=26 reports]`. The checker
assumes about one write per picture, so its "the camera held still on some pictures although it was written" (3 of 11
turning seconds on 10-30; 4 of 32 and 2 of 35 on 10-17) cannot tell a held camera from many writes of one value.
Proposed row `[PD]`: call the recorder's camera write once per picture, at the last write before the eye is drawn (not
on every engine camera set), then re-read the next headset log.
