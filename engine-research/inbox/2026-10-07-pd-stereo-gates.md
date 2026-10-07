# The stereo gates are r_fullscreen and the fullscreen refresh rate; fake IsActivated now answers an error

From: the `/lm` session's static reader helper, 2026-10-07. Follows the live fake-mode runs A (flag) and B (always 1):
gate A `[0xbc1daa]`=1, but `[0xbc1bb8]`=0 and `[0xbc1bec]`=0, and the game dropped to one eye both times. Nothing run
against the game here.

Supersedes: the "IsActivated answers the Activate flag" default of `2026-10-07-pd-fake-stereo-flag.md` (the flag
mode still exists behind a marker file).

## 1. What the gates are `[inferred-static 2026-10-07]`

- **`[0xbc1bec]` = `r_fullscreen`.** Written at `0x97bdb7` as `[0xdd0e30] != 0`; `0xdd0df0` is the cvar object
  registered with the name `r_fullscreen` (`0x9d30b2` → `pushl $0xdd0df0`), and a cvar's value sits at +0x40.
  Tefa's profile has `r_fullscreen "0"` (windowed, as our rule requires).
- **`[0xbc1bb8]` = the number in `r_fullscreen_refreshes`.** `0x97bfa1` runs `sscanf(<that cvar's string>, "%d",
  &[0xbc1bb8])`; the cvar object is `0xdd0ef8` (registered as `r_fullscreen_refreshes`, string at +0x3c). The profile
  has `r_fullscreen_refreshes "0"`. It is also the fullscreen refresh rate handed to D3D (`0x97c0b1`, only when
  `r_fullscreen` is on). So the 120 test is "fullscreen at 120 Hz", the 3D Vision requirement.
- **`[0xbc1daa]` = "the driver says stereo is enabled"** (`2026-10-07-pd-stereo-clear-fails.md`).
- **`0xdd1b58` is the `r_stereo_enable` cvar** (registered right after its name at `0x9dc115`/`0x9dc220`). The eye
  count each frame is 1 + (its value ≠ 0) (`0x9739ac`, through the per-view byte `[0xdcc134]`, copied from the cvar).

## 2. Why the game drops to one eye `[inferred-static 2026-10-07]`

`0x9731a0(want)` runs every frame with `want` = `r_stereo_enable`. After the early-out, it calls **IsActivated**;
**if that call succeeds**, it forces `want` off unless gate A, `r_fullscreen` and refresh 120 all pass, calls
Activate/Deactivate if the answer differs, and then **writes `want` back into `r_stereo_enable`** (`0x951770` on
`0xdd1b58`, a cvar setter). Windowed, `want` is always forced off, so the console setting is wiped to 0 and the eye
count drops to 1. That is runs A and B. **If IsActivated fails, it returns before any of that**, which is why the
pass-through run (real driver, -140) kept two eyes.

Device set-up (`0x9751e0`, gate A on) also creates the handle, asks IsActivated (answer ignored, byte preset 0), calls
`0x9731a0(r_fullscreen && refresh == 120)`, then sets `r_stereo_enable` to the cached state (0). So
`r_stereo_enable 1` has to be typed after loading, as before. It then calls id `0x6B9B409E` (handle, window,
3000), most likely SetNotificationMessage `[hypothesis]`.

## 3. The least invasive lever, chosen: fake IsActivated answers an error

Options weighed:
- **Config** (`r_fullscreen 1`, `r_fullscreen_refreshes 120`): makes the game want stereo, but needs fullscreen at
  120 Hz. Breaks the windowed rule and the monitor may not do 120. Rejected.
- **Writing the gate bytes from our dll:** works, but writes game memory and fights the settings code. Not needed.
- **IsActivated answers an error in fake mode (built):** no memory write, no config change. Gate A stays 1 (the
  second-eye surfaces are built) and the per-frame decision returns early, so `r_stereo_enable` alone runs the eye
  loop. Activate and Deactivate are never called, so the "Deactivate before the first Activate" question no longer
  matters. `[hypothesis]` until the run: the expected log is IsActivated -140 each frame (logged once, then only on
  change), the watch showing `r_stereo_enable=1`, eye count 2, gate A 1, SetActiveEye L/R about 120/s each, and in
  the d3d9 log no failed Clears and no NULL SetRenderTarget.

## Builds `[compile-verified 2026-10-07]`, not deployed

- `staging/hard-reset-vr/proxy-nvapi/build/nvapi.dll`, SHA-256 `f9d665cc8b418d6d...`
  (`f9d665cc8b418d6d460308af16c0db5b50518e1f398e57331d4b424455b55dfb`). Supersedes `593876cb...`. Same two exports.
  - Fake mode default: IsActivated → -140, the game's byte left alone. `nvapi_fake_activated_flag.txt` brings back
    the flag answer and `nvapi_fake_always_activated.txt` the always-1 answer.
  - id `0x6B9B409E` is now answered OK for the dummy handle, so the real driver never sees the dummy handle.
  - IsActivated is logged for the first 10 calls, then only when the answer changes (it runs every frame).
  - The watch line now also shows `r_stereo_enable`'s value (`0xdd1b98`) and names the gates.
- The d3d9 build is unchanged (`4fdd7e04...`).
- Self-tests `[verified-numerically 2026-10-07, n=1 each]`: nvapi `pass` 6/6, `fake` 11/11 (IsActivated -140 ×4, byte
  untouched), `flag` 11/11, `always` 11/11; d3d9 `sbs chain` with the new nvapi passes.

## Suggested run (FLAT)

Both dlls, `nvapi_fake_stereo.txt` only (no flag/always files), d3d9 log-only. Load in, type `r_stereo_enable 1`.
Then add `d3d9_sbs.txt` while running (re-read once a second) and look for two pictures side by side.
