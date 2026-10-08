# The nvapi stand-in's log labels have LEFT and RIGHT crossed (cosmetic)

From `/pd` (Tomb Raider), 2026-10-08.

`staging/hard-reset-vr/proxy-nvapi/src/nvapi_proxy.c` defines `EYE_LEFT 1` and `EYE_RIGHT 2`. NVIDIA's header
(`nvapi_lite_stereo.h`, `NV_StereoActiveEye`, read 2026-10-08) has `RIGHT = 1`, `LEFT = 2`. The d3d9 proxy was already
corrected on 2026-10-07 and passes the raw number through, so **the pictures are not affected**; only the stand-in's
own log lines (`SetActiveEye(LEFT)`, the per-5-s left/right counts) name the eyes the wrong way round.

Suggested fix: swap the two defines in the stand-in (one line each). The Tomb Raider copy
(`staging/tomb-raider-2013-vr/proxy-nvapi`) already uses NVIDIA's numbering.
