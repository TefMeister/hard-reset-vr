# Why the window freezes in stereo (static read), and a d3d9 stand-in that shows both eyes side by side

From: the `/lm` session's static reader helper, 2026-10-07. Follows the live result in
`dev-archive/recon/2026-10-07-two-eyes-and-loose-shaders/`. Nothing run against the game.

## 1. Does the game stop presenting in stereo? No, not in the code

All `[inferred-static 2026-10-07]`, from the shipped exe (base 0x400000):

- The D3D9 device pointer lives at `[0xbc1bfc]`. **Present is called from one place, `0x96aec0`**, with no stereo
  test: if `[0xbc1bec]` is non-zero (this looks like a fullscreen flag `[hypothesis]`), `Present(NULL,NULL,NULL,NULL)`;
  otherwise `GetClientRect` on the window `[0xbaf8b4]`, then `Present(rect or NULL, NULL, window, NULL)`.
- All three frame paths that draw the world (`0x975880` called from `0x9778f3`, `0x978836`, `0x97907e`) end with
  `EndScene` and then `0x96aec0`. **The eye count does not change that.**
- **Frame start, `0x96af70`:** BeginScene, `GetBackBuffer(0,0,MONO,&[0xdcbe20])`, `SetRenderTarget(0, back buffer)`,
  then **for each eye:** `SetActiveEye`, that eye's own depth surface (`[0xdcbb9c + 0x24*eye]`, falling back to
  `[-0x48]`), viewport, `Clear`.
- **Final pass, inside `0x975880` at `0x976d30`:** for each eye, `SetActiveEye` (eye 0 → 2 = RIGHT, eye 1 → 1 = LEFT),
  then `SetRenderTarget(.., [0xdcbe20])`: **both eyes draw into the same back buffer, right first, then left.** There
  is no driver-only surface and no second swap chain. A 3D Vision driver would have split them; without it the left
  eye simply lands on top of the right.
- **`[0xbc1bec]` is also one of the three stereo-activation gates** (`0x9731a0`, see
  `2026-10-07-pd-fake-stereo-flag.md`), so on top of the 120 Hz test, driver stereo is only ever switched on when
  that flag is set, which is probably fullscreen `[hypothesis]`.
- **Correction to the live log** `[inferred-static 2026-10-07]`: the "IsActivated -140 (activated=1)" lines were
  printed by the old nvapi build, which read the answer byte even on failure. The game passes its own wanted state
  in that byte, so the 1 was the game's wish, not the driver's answer. The 2026-10-07 nvapi build prints -1 on
  failure. The log also shows no `CreateHandle`, `IsEnabled` or `Enable` call: the start-up seems to stop after
  `SetDriverMode` returns -219, so the handle stays NULL `[inferred-static 2026-10-07, from the live log]`.

**So the freeze is not explained by the code path.** Possibilities the new d3d9 log separates `[hypothesis]`:
(a) Present runs but fails (the log counts failures and HRESULTs); (b) Present succeeds but draws/clears into the back
buffer fail, so the old picture stays (the log counts draws and clears into the back buffer and Clear failures);
(c) Present is not reached at all (the d3d9 log goes silent while the nvapi log keeps counting eyes); (d) something
outside D3D, such as the window message loop.

## 2. The capture point chosen, and why

Simplest point: **the eye change itself**, since the back buffer then holds the eye that just finished. The nvapi
stand-in already sees every `SetActiveEye`, so it calls our d3d9's `hrvr_on_active_eye(eye)` on the render thread
(looked up by full path beside the exe, because the system `d3d9.dll` has the same name). The d3d9 stand-in copies
the back buffer into that eye's half of a double-width surface, but only if something was drawn or cleared into the
back buffer since the last change (the frame-start clears are copied too, then overwritten by the final pass). At
Present it copies the last eye, stretches the double surface over the back buffer, and presents. Frames with no eye
change are not touched.

- Watched device methods (method-table patch, real d3d9 does all the work): Present, Reset (drops our surface first),
  GetBackBuffer, SetRenderTarget, Clear, the four Draw methods.
- Switch: `d3d9_sbs.txt` beside the exe. Without it: log only. Log: `d3d9_proxy_log.txt`, a line a second.
- Self-test with no game `[verified-numerically 2026-10-07, n=1 each]`: `log` 7/7, `sbs` 8/8, `sbs chain` (eyes
  passed through our nvapi.dll exactly as in the game) 9/9: left eye in the left half, right eye in the right half,
  the window showed left | right, a mono frame untouched. StretchRect worked inside a scene on the dev PC's driver.
- Known limits `[hypothesis]`: a multisampled back buffer may refuse the final stretch (logged as "compose" failures);
  the HUD is probably drawn per eye, but if it is drawn after the loop it lands only in the left half.

## Builds `[compile-verified 2026-10-07]`, not deployed

- `staging/hard-reset-vr/proxy-d3d9/build/d3d9.dll`: SHA-256 `ca21c86a78e5b26b...`
  (`ca21c86a78e5b26b218a211ebcc0de34460da95274b24c0aab4e45f809ef7d07`). Exports: `Direct3DCreate9`,
  `Direct3DCreate9Ex` and the seven `D3DPERF_*` (passed through), plus `hrvr_on_active_eye` and `hrvr_get_sbs_surface`.
- `staging/hard-reset-vr/proxy-nvapi/build/nvapi.dll`: SHA-256 `593876cb8aa50691...`
  (`593876cb8aa506910dc104ac2c1e9dfc1c3746b014fb551ff47c93d5600316c5`). Same two exports as before; its tests still pass
  6/10/10. This build supersedes `cfd70f90...` from `2026-10-07-pd-fake-stereo-flag.md`.

## Suggested run (FLAT)

Both dlls beside the exe, nvapi in pass-through, no `d3d9_sbs.txt` first: turn `r_stereo_enable 1` on and read the
d3d9 log against (a) to (d). Then add `d3d9_sbs.txt` and look at the window for two pictures side by side.
