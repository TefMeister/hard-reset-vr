# Faster headset handover: the 14 ms was LockRect waiting; an async readback takes ~1 ms

From: the `/lm` session's static reader helper, 2026-10-07. Nothing run against the game here. Follows the live
simulator run (`dev-archive/recon/2026-10-07-in-the-headset-simulator/`, d3d9 `ae49c7b1b487`): readback 13.6-14.8 ms,
~40 of 60 frames handed over.

Supersedes: inbox `2026-10-07-pd-openxr-bridge.md`, the line that the WAIT readback is "never waited for". It waits,
in LockRect.

## Where the time went `[verified-numerically 2026-10-07, n=1 run each]`

New per-part timers (GPU copy / GetRenderTargetData / LockRect / memcpy), self-test at the game's size (two
1280x720 eyes), 60 frames/s, a GPU kept busy with 60 extra full-screen clears per eye, 32-bit OpenXR simulator:

| Readback | GPU copy | GetRenderTargetData | LockRect | memcpy | total per Present | frames handed over |
| --- | --- | --- | --- | --- | --- | --- |
| WAIT (old, default) | 0.00 | 0.01 | **4.2-6.2 avg, max 10.4** | 0.96 | 5.1-7.1 avg, max 11.3 | 60/60 |
| ASYNC (new, switch) | 0.00 | 0.01 | **0.00** | 0.96 | **0.95-1.0 avg, max 1.35** | 55-60/60 (2 typical) |

- GetRenderTargetData itself returns at once on this driver (it is queued); the old way's cost is LockRect waiting
  for that copy, which sits behind the whole current frame on the GPU. In the game the frame is heavier, hence 14 ms
  `[inferred-static 2026-10-07]` (the live game run had no per-part timers).
- ASYNC never waits: LockRect only after the slot's event query says the copy landed. The frames it misses are not
  stalls; two copies sometimes land in the same Present and only the newer one is handed over (counted as `dropped`).
  The headset still gets 60 submitted frames/s. Ring 4 did not improve on ring 3 (55-59/60 against 58-60/60, n=1) -
  it is latency, not slots.
- **Idea (1), reading back each eye at its capture, was not built:** the two-eye surface is two un-stretched
  1280x720 halves (StretchRect 1:1 into each half), so it is the same bytes; it would split one wait into two waits.
  The async route removes the wait instead.
- **Idea (2), a deeper ring:** built as `readback_ring=` (2..8) in `d3d9_vr.ini`; it does not help the WAIT way
  (the wait is on the copy issued this frame) and is not needed by ASYNC.

## D3D9Ex (zero-copy) - not built yet, the question is now instrumented

- Static `[inferred-static 2026-10-07]`: the exe imports `d3dx9_43`; its 9 D3DX texture-creation calls ask for pools:
  TextureFromFileInMemoryEx 0x971162 = DEFAULT, 0x97292f = SYSTEMMEM, 0x972ec4 = `ebx` (very probably 0, the same
  register as Usage); CubeFromMemEx 0x9710f2 = DEFAULT (eax = 0 there), 0x9728d6 = SYSTEMMEM; VolumeFromMemEx 0x971125
  = DEFAULT, 0x972903 = SYSTEMMEM; D3DXCreateTexture 0x977174 = `esi` with Usage RENDERTARGET (so DEFAULT);
  D3DXCreateCubeTexture 0x9783a4 = SCRATCH. **No MANAGED among them.** The SYSTEMMEM loads followed by a copy to DEFAULT
  is the D3D9Ex-friendly pattern. The game's own device CreateTexture / CreateVertexBuffer / CreateIndexBuffer calls
  could NOT be read statically (no symbols; the call sites are indistinguishable from other COM calls), so this is open.
  Tool: `staging/hard-reset-vr/proxy-d3d9/tools/d3dx_pool_scan.py`.
- Run-time answer, built: the d3d9 stand-in now counts every CreateTexture / Volume / Cube / VertexBuffer /
  IndexBuffer / OffscreenPlainSurface by pool (always on, changes nothing): `created so far by pool
  (DEFAULT/MANAGED/SYSTEMMEM/SCRATCH/other) ...; MANAGED total N`, and the first 8 MANAGED creations in full.
  Self-test: a MANAGED texture is counted and described `[verified-numerically 2026-10-07, n=1]`.
  **If the next live run says MANAGED total 0 after loading a level, the D3D9Ex shared-surface route is open**
  `[hypothesis]`; if not, it needs MANAGED to be emulated, which is a much bigger job. Given ASYNC's ~1 ms, it may not be
  needed at all.

## Build `[compile-verified 2026-10-07]`

`staging/hard-reset-vr/proxy-d3d9/build/d3d9.dll`, SHA-256 `2fbd17857ae06868...`
(`2fbd17857ae068684d4c1055f65e56074b98e7a3a4e180b1de38aa92488326a4`). Supersedes `ae49c7b1b487`. Same 11 exports, same
imports. Self-tests: log 10/10, sbs 12/12, sbs chain 13/13, xr WAIT and xr ASYNC (big fast load=60) pass, handover
11/11, formats 7/7.

- **New switch:** `d3d9_readback_async.txt` beside the exe, re-read each second (WAIT stays the default). It can be
  flipped during play to compare the two ways in the same session.
- Log line now: `headset per s (ASYNC|WAIT, ring N): eyes read back, frames handed over X of Y, not ready, dropped,
  failed; readback ms per Present avg/max = GPU copy + GetRenderTargetData + LockRect + memcpy (avg/max each); headset
  frames submitted, empty, pictures uploaded`.

## Suggested run (FLAT, dev PC, simulator)

Same install as the simulator run, new d3d9 only. Play with WAIT for ~20 s, then drop `d3d9_readback_async.txt` in.
Expect the LockRect column to fall from ~13 ms to ~0, the total to ~1-2 ms, and handed over to approach 60 of 60.
After a level loads, read the `created so far by pool` line for MANAGED.
