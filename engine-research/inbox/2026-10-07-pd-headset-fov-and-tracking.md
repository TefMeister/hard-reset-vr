# The headset's own lens and head tracking, inside Hard Reset's camera

From: the `/lm` session's static reader helper, 2026-10-07. Nothing run against the game here. Modelled on The Evil
Within's `b4ab740` (head turn as a clip-space correction measured from draws), but Hard Reset lets us do better: the
game's own camera object holds view and per-eye projections separately, so the turn and the lens go in BEFORE the
game multiplies them, and before culling.

## Where the matrices live `[inferred-static 2026-10-07]`

Read from `hardreset.exe` at its fixed base (tool: `staging/hard-reset-vr/proxy-d3d9/tools/disasm_range.py`).

- **The perspective camera class**, method table `0xa8df64` (built at `0x9a9ae0`). Only one table points at the two
  methods below (no subclass overrides were found).
- **Slot 25 = `0x9a9770`, the per-frame matrix update** (thiscall, no stack arguments). It writes into the camera:
  - `+0x2c` vertical fov in radians (`+0x380` × `[0xdcfd5c]` × π/180);
  - `+0x34` near (`r_nearZ`) and `+0x38` far;
  - `+0x40` the **view** (world → camera), copied each frame from the scene node (`[0xad6574]+4 + idx·0xa0 + 0x40`),
    so a change to it never builds up over frames and never reaches gameplay;
  - `+0x200`, `+0x240`, `+0x280` the **eye 0 / eye 1 / mono projections**: sy = 1/tan(fov/2), sx = sy ×
    `[0xbc1bc0]`/`[0xbc1bbc]` (height/width), m22 = f/(n−f), m23 = −1, m32 = n·f/(n−f) (D3DX PerspectiveFovRH).
    The eyes add m20 = −sign·S and m30 = −sign·S·conv, with sign −1 for eye 0;
  - `+0x2c0`, `+0x300`, `+0x340` view × projection, from `0x9a8ab0` (out = A × B, row vectors);
  - `+0x80..` and `+0x140..` the inverses of the projections and of the products, from `0x9a8bc0` (a full 4x4
    cofactor inverse).
- **Slot 26 = `0x9a9dd0`, publish.** It copies view, the three projections, the three products, near, far, fov, S and
  conv into the render frame `0xdcbec0 + 0x560 × ([0xdcca58] ^ [0xdcca60])`. The renderer reads frame `[0xdcca58]`
  (`0x978211`). So the game writes one frame while the renderer reads the other.
- **Conventions:** row vectors (`mul(pos, M)`, as the shaders also say); a right-handed view space with x right,
  y up and −z forward; depth runs 0..1. That is OpenXR's own view frame, so the headset quaternion needs no axis
  flips (The Evil Within's frame needed them).
- These matrices reach the picture `[verified-live 2026-10-07]`: the game's own eye shift lives in exactly these
  eye projections, and it produced the 32 px separation measured in the window. Whether culling reads the camera's
  mono product `+0x340` is `[hypothesis]`.

## What was built `[compile-verified 2026-10-07]`

d3d9 `f321323f9bbe` (`f321323f9bbe9b2a51754e96d56cb38775ebc1c9cb8166bb1e070a62e364b643`), supersedes
`2fbd17857ae0`. Same 11 exports. The proxy patches table slots 25 and 26, and only after checking that the exe is
`hardreset.exe` at 0x400000 and that those slots hold `0x9a9770` / `0x9a9dd0`; otherwise it logs a refusal.

- **`d3d9_headset_fov.txt`** (off by default) — after the game's own update:
  - each eye projection becomes T(−e)·Rrel·P(fov). P(fov) is the headset's asymmetric lens from xrLocateViews, built
    the game's way; e is the eye's offset from the head (IPD, in game units); Rrel covers canted displays.
  - The game's own S/conv shear is **replaced, not added to**.
  - The mono projection becomes a lens covering both eyes plus `cull_margin_deg` (5), so the game culls for the wider
    headset view.
  - The products and inverses are rebuilt as the game builds them. If any inverse fails, nothing is written.
- **`d3d9_head_track.txt`** (off by default):
  - the camera's view becomes View·T(−c)·R(head), so the turn is in place before culling and before publish.
  - c is the head's movement since tracking was switched on × `units_per_metre`, used only with `head_position=1`.
  - The pose a frame was built with is stored per render frame at publish, picked up at the renderer's first eye
    change (`[0xdcca58]`), carried through the readback with that picture, and submitted as the layer's pose and fov.
    The runtime then corrects only for the time since drawing.
- **Only stereo cameras are touched:** `cam+0x385` set, and published in the last 0.5 s.
- **Log once a second:**
  - `headset pose #N: yaw/pitch/roll, head position, left eye fov` — what the headset sent;
  - `head per s (lens, tracking): poses, camera updates (stereo, cameras seen), published (with pose), patched L/R/cull,
    refused (not stereo / not published / no pose / inverse), render frames with/without pose (read/write index)`;
  - `head pose last applied: yaw/pitch/roll, offset, IPD mm, both lenses in degrees, the game's fov/near/far/
    separation, screen size, the camera's world position`;
  - `headset frames submitted with the pose their picture was drawn with: N`.
- **Settings in `d3d9_vr.ini` `[xr]`:** `units_per_metre=1.0`, `head_position=0`, `cull_margin_deg=5`.

## Tested without the game

- **Maths (`test/hr_head_math_test.c`), 15/15** `[verified-numerically 2026-10-07, n=1]`:
  - the game's symmetric projection is rebuilt exactly (max diff 6e-8);
  - an asymmetric lens puts its four edge directions on ndc ±1, and near/far on depth 0/1;
  - yaw +30 (left): a point 30° to the left becomes centred, and straight ahead moves right;
  - pitch +20: a point 20° up is centred; roll +15: a point on the horizon to the right drops;
  - a right eye 32 mm right of the head sees a point 2 m ahead 0.016 ndc to its left, also with the head turned 90°;
  - the turned view matches an independent look-at build over 2,000 random poses and game views;
  - a planted wrong-way turn is told apart (the test can fail);
  - the culling lens covers both eyes; the logged angles read back correctly.
- **The headset side, against the 32-bit simulator** `[verified-numerically 2026-10-07, n=1]`: the simulator was set
  to yaw 30, pitch 10, roll 5 at (0.1, 1.7, 0). The log read exactly "yaw 30.0 pitch 10.0 roll 5.0, head at (0.100,
  1.700, 0.000)". The simulator's eye lens is −54.0/40.0/44.0/−54.3° (left eye: left, right, up, down).
- **All earlier self-tests still pass.** The async check now asks "LockRect never waits and 75%+ of frames handed
  over". The simulator lets 50–60 of 60 through depending on GPU load, which made the earlier 90% bar flaky.
- **Fixed a test bug, not a product bug:** the handover test's reader could pick up the partial frame left by the
  single-thread phase (about 1 run in 30). Now 0 in 60. A memory barrier was also added before publish.

## Not known yet

- **The game's units per metre.** Havok physics suggests metres `[hypothesis]`. The camera's world position is now
  logged, so walking a known distance measures it. Until then head movement stays off, and the IPD with the lens on
  is 64 mm × 1.0 = 0.064 units.
- **Whether other perspective cameras share this class** (cutscenes, reflections) and also publish. The `cameras
  seen` count will say.
- **The HUD:** it is drawn flat over each eye, its own per-eye shift still comes from S, and it will look stretched
  across the headset's lens.

## Suggested run (FLAT/simulator, dev PC)

1. With the current install (async readback, OpenXR, simulator), add `d3d9_headset_fov.txt` and `d3d9_head_track.txt`,
   then load in and type `r_stereo_enable 1`.
2. In the log, expect `head: camera update ... wrapped`, `patched L/R` near the frame rate, and `render frames with
   pose` near the frame rate.
3. Set the simulator to yaw 30. Expect the log to show yaw 30.0 applied, the world in the window to swing RIGHT (the
   view turned left), and the simulator view to stay world-fixed.
4. Then pitch and roll, then walk a measured distance to read `units_per_metre` from the camera position.
