# Why the stereo Clears fail: the second eye's surfaces are never made, because the real driver says "no stereo"

From: the `/lm` session's static reader helper, 2026-10-07. Follows the live log-only run (d3d9 `ca21c86a`,
nvapi `593876cb`, pass-through): Present 60/s with 0 failures, eye calls 120/s each, failed Clears 120/s with
0x8876086c (D3DERR_INVALIDCALL), the window updating but smeared and over-bright. Nothing run against the game here.

⚠️ Reading that log: the old "fail" counter counted **every** failed Clear, not only those of the back buffer, and
"clears of back buffer" also counted failed ones. So "all back-buffer clears fail" is not shown; 120 failures a second
are. The new build splits them.

## The chain `[inferred-static 2026-10-07]`

1. **Start-up, `0x973688`:** `[0xbc1daa] = 0`, then Initialize → **SetDriverMode(2)** → if that succeeds,
   **Stereo_IsEnabled(&[0xbc1daa])** (`0x6cbcd0`, ID `0x348FF8E1`) → if enabled, Enable (`0x6cbb70`), IsEnabled again,
   then one more NVAPI call (`0x6cb870`, ID `0xBE7692EC`, which our proxy does not wrap; its answer is ignored).
   **So `[0xbc1daa]` = "the driver says stereo is enabled".** With the real driver, SetDriverMode returns -219, so it
   stays 0 (the live log shows no IsEnabled/Enable calls, which fits).
2. **Render-surface set-up, `0x970480`** (called from `0x975684` and `0x97c20a`): builds a table of 0x24-byte surface
   records from `0xdcbb50` (width, height, format, then the D3D objects). The depth record at `0xdcbb50` (screen size,
   INTZ / RAWZ / D24S8) and, if `[0xdd2dd0] > 0`, a supersampled one at `0xdcbb98`. **Only if `[0xbc1daa] != 0`
   (`0x970aaf`) does it make the second eye's copies:** `0xdcbb74` (copy of `0xdcbb50`), `0xdcbbbc` (copy of
   `0xdcbb98`), `0xdcbd00` (copy of the scene target `0xdcbcdc`), and more after it.
3. **Frame start, `0x96af70`, eye 1 (LEFT):** depth = `[0xdcbbc0]`, else `[0xdcbb78]`. Both are NULL, so
   **SetDepthStencilSurface(NULL)**, then **Clear(flags 7 = colour + depth + stencil)** with no depth surface: that is
   exactly D3DERR_INVALIDCALL. The flags are 1 (colour only) when `[0xdd2dd0]` is non-zero, 7 otherwise.
4. **World pass, `0x8a6b60`, eye 1:** the same NULL depth, and **SetRenderTarget(0, `[0xdcbd04]` = NULL)**, which
   D3D9 refuses, so eye 1's scene is drawn into whatever target was still bound, over eye 0's. That fits the
   over-bright smear `[hypothesis]`.

Eye 0 uses the records that do exist, so its Clears should succeed. Two failures per frame (frame start + a world
pass Clear for eye 1) would give the 120/s seen `[hypothesis]`.

## What to do

- **Main lever, no d3d9 workaround needed** `[hypothesis]`: start the game with our nvapi.dll in **FAKE mode**
  (`nvapi_fake_stereo.txt`). Fake mode answers SetDriverMode 0 and IsEnabled 1, so `[0xbc1daa]` becomes 1 and the
  second-eye surfaces are built. ⚠️ Whether `0x970480` runs after the start-up check is not proven; if the first run
  still shows NULL second-eye surfaces, a resolution change (which rebuilds them) should fix it. Fake mode also makes
  the game create a stereo handle (a dummy one), and `[0xbc1daa]` is gate A of the activation decision.
- **The new d3d9 log proves or disproves this** in log-only mode: the first 12 failed Clears are logged in full
  (flags, render target, depth surface or NONE, viewport, current eye). It also counts per second: failed Clears of
  the back buffer, failed Clears with no depth bound, SetRenderTarget calls that are NULL or failed, and depth surfaces
  set to NULL. Prediction for pass-through: failures on eye 1 (LEFT) only, depth NONE, flags 7, plus a NULL
  SetRenderTarget per frame. Prediction for fake mode: none of these.
- **Fallback switch `d3d9_clear_fix.txt`:** a failed colour+depth Clear is retried colour-only. It stops the smear
  from the Clear, but cannot fix the missing eye-1 scene target, so it is a stop-gap only.
- `d3d9_sbs.txt` and `d3d9_clear_fix.txt` are now looked for again once a second (at a Present), so either can be
  switched on or off while the game runs; the log says when one changes.

## Builds and tests

- `staging/hard-reset-vr/proxy-d3d9/build/d3d9.dll`, SHA-256 `4fdd7e04b0b49670...`
  (`4fdd7e04b0b49670274e9a1e9fecdd6c4fdf166586b863442b6c777e5d5dca35`) `[compile-verified 2026-10-07]`. Supersedes
  `ca21c86a...` from `2026-10-07-pd-eye-capture-proxy.md`. Exports unchanged. The nvapi build is unchanged
  (`593876cb...`).
- Self-test `[verified-numerically 2026-10-07, n=1 each]`: `log` 9/9, `sbs` 10/10, `sbs chain` 11/11. New checks: a
  colour+depth Clear with no depth surface fails with the same 0x8876086c as in the game; after `d3d9_clear_fix.txt`
  is added **while running**, the next look picks it up and the retry clears the colour.
