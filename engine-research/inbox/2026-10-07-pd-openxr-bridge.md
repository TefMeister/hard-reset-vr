# Eye order fixed (our labels were swapped) + headset output from the d3d9 stand-in

From: the `/lm` session's static reader helper, 2026-10-07. Nothing run against the game here.

Supersedes: dossier §"STEREO SIDE BY SIDE IN THE WINDOW, WITH REAL DEPTH", the line "Halves possibly swapped (eye 0 is
RIGHT) `[hypothesis]`", and the 2026-10-01 reading "SetActiveEye(handle, idx 0 → 2, 1 → 1)" as meaning eye 0 = RIGHT.
The values are right; the NAMES we gave them were wrong.

## 1. Eye order: the halves WERE swapped, and why

- **NVAPI numbers the eyes RIGHT = 1, LEFT = 2, MONO = 3** (`NV_StereoActiveEye` in NVIDIA's `nvapi_lite_stereo.h`,
  as vendored in RenderDoc's tree) `[reported]`. Both our proxies defined `EYE_LEFT 1`, `EYE_RIGHT 2`: backwards.
- So the game's **eye 0 calls SetActiveEye(2) = LEFT** and eye 1 calls SetActiveEye(1) = RIGHT `[inferred-static
  2026-10-07]` (2026-10-01 trace + the header). Eye 0 has sign −1 in clip.x += sign·S·(w − conv), which is exactly
  NVIDIA's 3D Vision convention (left eye −1): far things (w > conv) move LEFT in the left eye. Consistent.
- Our first d3d9 build put value 1 (truly RIGHT) in the left half. Predicted: in the left half, far scenery sits
  further RIGHT than in the right half. The live measurement L[x] ≈ R[x−32] says exactly that (far 32 px, gun ~+3 px,
  just beyond the 0.35 convergence) `[measured 2026-10-07]`. Three independent lines agree: **the window was
  right | left**.
- **Fixed in d3d9** (`EYE_RIGHT 1`, `EYE_LEFT 2`): value 2 now lands in the left half. Switch `d3d9_swap_eyes.txt`
  beside the exe crosses them back, window and headset, re-read each second. **Default (no file) = the correct
  order** `[compile-verified 2026-10-07]`; self-test: eye 2 → left half, eye 1 → right half, and the file added while
  running crosses them `[verified-numerically 2026-10-07, n=1]`. Expected live: far scenery now further LEFT in the
  left half (L[x] ≈ R[x+32]) `[hypothesis]`.
- ⚠️ Our `nvapi.dll` (`1921f0ddd086`, not rebuilt) still LOGS the eyes with swapped names ("left 597, right 597" is
  fine as counts, but "SetActiveEye(LEFT)" lines mean RIGHT). It passes the raw value on, so nothing it does is wrong.
  Fix the labels next time it is rebuilt.

## 2. Headset output (OpenXR) from the d3d9 stand-in `[compile-verified 2026-10-07]`

- Off by default; **on with `d3d9_openxr.txt`** beside the exe (checked each second; starts the headset thread once).
- **Headset thread** with its own D3D11 device and session, the only thread calling OpenXR (shape from our Metro and
  Evil Within bridges). Each eye goes out as a **projection view** (pose + FOV from xrLocateViews), not a quad.
- **Handover on the CPU** (D3D9 non-Ex surfaces cannot be shared with D3D11): at each Present the two-eye surface is
  copied on the GPU into a ring of 3 render targets with an event query after each copy; the **oldest copy whose query
  says done** is read back (GetRenderTargetData → LockRect → split into two eyes) into a 3-slot handover. The lock is
  held only to swap slot numbers, so neither thread waits; if no copy is ready the frame is skipped and counted.
  Headset thread: takes the newest frame, forces alpha opaque (X8R8G8B8), swaps red/blue only if the runtime offers
  no BGRA format, uploads into a held texture per eye, copies that into each headset frame's swapchain image.
  Swapchain format preference: B8G8R8A8_UNORM_SRGB (the game's picture is already gamma-encoded), then R8G8B8A8_SRGB,
  then the UNORM ones.
- **Log, once a second:** `headset per s: eyes read back, frames handed over, not ready, failed, readback ms avg/max;
  headset frames submitted, empty, pictures uploaded; headset <stage>`.
- **Settings:** `d3d9_vr.ini` `[xr]` `runtime_json=` (this process only) and `test_pattern=1` (red | blue).
- **What must sit beside `hardreset.exe` for the headset:** our `d3d9.dll` + `nvapi.dll` (as now, fake mode),
  `d3d9_openxr.txt`, the **32-bit** `openxr_loader.dll` (OpenXR.Loader NuGet 1.0.10.2, `native/Win32/release/bin/`,
  SHA-256 `fb1e06de965390f9...`; a copy sits in the XIII project's third_party), and on the dev PC a `d3d9_vr.ini`
  with `runtime_json=` pointing at the OpenXR simulator's `openxr_simulator-32.json` (in the tools folder). The runtime must be a
  32-bit one: on the home PC that means checking SteamVR/the headset runtime publishes a 32-bit json `[hypothesis]`.

## Self-tests (no game)

- Pure: handover 11/11 (two threads, 2 s: 3.3 M frames written, 300 k read, 0 torn, 0 out of order, writer never
  without a slot); formats 7/7 `[verified-numerically 2026-10-07, n=1]`.
- `d3d9_selftest log` 9/9, `sbs` 11/11, `sbs chain` (with nvapi `1921f0ddd086`) 12/12.
- `d3d9_selftest xr <simulator 32-bit json>` 13/13 with 320x180 eyes: session runs, swapchains format 91 (BGRA sRGB),
  ~30 frames/s handed over (the test's own pace), ~60 headset frames/s submitted, readback 0.9-4 ms avg, max 9.8 ms
  on the first second `[verified-numerically 2026-10-07, n=2]`. The simulator's screenshot showed **left eye green,
  right eye blue**, exactly what the test drew per eye, colours not swapped `[verified-numerically 2026-10-07, n=1]`
  (`staging/hard-reset-vr/proxy-d3d9/test/evidence/`).
- Not known: the readback cost at the game's real size (2560x720, 16x the test) and whether it slows the game
  `[hypothesis]` — the per-second ms line answers it. The picture keeps the game's own lens (FOV), not the headset's,
  and the camera does not follow the head yet.

## Build

`staging/hard-reset-vr/proxy-d3d9/build/d3d9.dll`, SHA-256 `ae49c7b1b48741f4...`
(`ae49c7b1b48741f47d555967566258d6c3652fe7d7e697b46ff4d139ae681e8a`). Supersedes `4fdd7e04b0b4`. Same 11 exports;
imports only KERNEL32 + the C runtime (d3d11/dxgi/the loader are loaded at run time, only when the headset is on).

## Suggested runs (FLAT, dev PC)

1. Same as the working run, new d3d9 only: the halves should now be left | right (far scenery further LEFT in the
   left half). If not, `d3d9_swap_eyes.txt` and say so.
2. Add `d3d9_openxr.txt`, the 32-bit loader and `d3d9_vr.ini` (simulator): expect `xr: session running`, the
   simulator window showing both eyes, and the `headset per s:` line; read the readback ms and the game's fps.
