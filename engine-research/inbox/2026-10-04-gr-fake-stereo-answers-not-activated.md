# Before the `r_stereo_enable` launch: our fake nvapi always answers "stereo NOT activated"

From: `/gr`, 2026-10-04. Read our own `staging/hard-reset-vr/proxy-nvapi/src/nvapi_proxy.c` against the wiz3D
finding already in `external-research/topics/2026-09-29-hard-reset-is-a-3d-vision-direct-mode-game.md`. Nothing run.

- **wiz3D's Hard Reset fix** (PR #29, maintainer-confirmed) `[reported]`: the game calls `Stereo_Deactivate` at
  start-up to mean "I draw my own stereo", later asks `Stereo_IsActivated`, and **drops to mono if the answer is
  no**, never reaching `Stereo_Activate` or `SetActiveEye`. Their stand-in ignores a Deactivate that arrives before
  the game's first Activate, and then reports "activated".
- **Ours, in fake mode** (`nvapi_fake_stereo.txt`): `Stereo_IsActivated` always writes `activated=0`, and
  `Activate`/`Deactivate` only return success; nothing remembers an Activate `[inferred-static 2026-10-04, read of
  the source]`. If the game behaves as wiz3D saw, the fake mode reproduces exactly the failure they fixed.
- **In pass-through mode** (the board's `[FLAT]` row as written) the dev PC's real driver refuses direct mode
  (-219) and reports stereo off (the proxy README), so that run measures the same "no" from the real driver.
- **Our own dossier says the eye loop runs from the cvar alone** (driver stereo is activated only if the driver
  reports enabled and `[0xbc1bb8] == 120`) `[inferred-static 2026-10-01]`. That and wiz3D's report disagree about
  whether an "activated = no" answer stops the eye loop; the launch decides it.
- **Suggested before the launch:** in fake mode, keep a flag that `Stereo_Activate` sets and only a Deactivate
  *after* the first Activate clears; have `IsActivated` report that flag (or simply 1). Then run the board's
  `[FLAT]` row twice, pass-through and fake, and compare the `SetActiveEye` counts. Also worth logging: the value
  at `[0xbc1bb8]` (the 120 check looks like a refresh-rate test, which a 60 Hz desktop would fail) `[hypothesis]`.
- Also from wiz3D's `NvDirectMode/ReadMe.txt`, for whoever builds the eye capture `[reported 2026-10-04]`: its
  DX9 route pairs a `d3d9.dll` proxy with the `nvapi.dll` stand-in, the two sharing the active-eye state; the proxy
  sends each eye's draws to one half of a side-by-side surface. Known limits: windowed only, and a device Reset
  does not re-double the surface. Read only; nothing copied (LGPL).
