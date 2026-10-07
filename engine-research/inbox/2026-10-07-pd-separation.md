# The game shifts each eye itself (3D Vision formula); separation came from our fake answers, which were 0

From: the `/lm` session's static reader helper, 2026-10-07. Follows the first side-by-side picture (nvapi
`f9d665cc` fake + d3d9 `4fdd7e04` with `d3d9_sbs.txt`): two full pictures, but the halves nearly identical (best
shift 0 px, far and near). Nothing run against the game here.

Supersedes: the 2026-10-01 modding note's line "the world's eye shift was the 3D Vision driver's job"
(`modding-notes/2026-10-01-pd-the-game-draws-two-eyes-from-a-console-setting.md`, "Later the same session"). The game
builds per-eye projections itself.

## How the game uses separation and convergence `[inferred-static 2026-10-07]`

- **The four settings** (names tied to objects by their registration code, value at +0x40 int / +0x44 float):
  `r_stereo_eye_separation` = `0xdd1a50` (default "0.0"), `r_stereo_separation` = `0xdd1aa8` (default "0.0"),
  `r_stereo_convergence` = `0xdd1b00` (default "0.35"), `r_stereo_enable` = `0xdd1b58` (default "0"). `r_nearZ`
  defaults to 0.15.
- **Device set-up (`0x9751e0`), driver stereo enabled only:** `GetEyeSeparation` (ID `0xCE653127`) →
  `r_stereo_eye_separation`; `GetSeparation` (ID `0x451F2134`) × 0.01 → `r_stereo_separation`. Each one is skipped if
  a flag bit on that setting is set (`[0xdd1a5c]`, `[0xdd1ab4]`); probably "set by the user" `[hypothesis]`. The game
  never asks for the driver's convergence; it uses its own `r_stereo_convergence`.
- **Per camera (`0x9a980b`..`0x9a9870`):** stereo is on for a camera if `r_stereo_enable` ≠ 0 and |convergence| >
  1e-38; then `S = r_stereo_separation × r_stereo_eye_separation` (`[cam+0x388]`), convergence at `[cam+0x38c]`.
- **Per eye (`0x9a9975`..`0x9a9a7e`):** the game builds eye 0 (sign −1) and eye 1 (sign +1) projection matrices with
  `m[2][0] = −sign·S` and `m[3][0] = −sign·S·convergence`. With its right-handed projection (w = −z_view) that is
  **clip.x += sign · S · (w − convergence)**, NVIDIA's 3D Vision formula. Objects at the convergence depth have no
  shift; far scenery approaches ±S in clip space, which is S/2 of the picture width per eye. These matrices go into
  the per-view slots `0xdcbf40`/`0xdcbf80`, `0xdcc000`/`0xdcc040` (`0x9a9e01`..) that the frame copies per eye.
- **So with our fake answers of 0.0, S = 0** and both eyes were identical, matching the live result. Tefa's earlier
  `r_stereo_eye_separation 5` showed nothing because `r_stereo_separation` was still 0 (S is the product).

## What was built `[compile-verified 2026-10-07]`

- Fake mode answers **GetSeparation 50 (%)** and **GetEyeSeparation 0.1** by default, so **S = 0.5 × 0.1 = 0.05**:
  far scenery about 2.5% of the picture width apart per eye (about 32 px in a 1280 window, 64 px between the eyes).
  The gun near the convergence depth (0.35) shifts little. Values come from `nvapi_stereo.ini` beside the exe
  (`[stereo] separation_percent=`, `eye_separation=`); a sample is in `staging/hard-reset-vr/proxy-nvapi/`. The log
  states the values and the resulting S at start-up.
- The once-a-second watch now logs `r_stereo_separation`, `r_stereo_eye_separation`, their product S, and
  `r_stereo_convergence` straight from the game's settings, so the run shows what the game really uses.
- The console still works after loading: `r_stereo_separation 0.5`, `r_stereo_eye_separation 0.1`,
  `r_stereo_convergence 0.35` would have the same effect without the ini `[hypothesis]`.

## Builds and tests

- `staging/hard-reset-vr/proxy-nvapi/build/nvapi.dll`, SHA-256 `1921f0ddd08643a3...`
  (`1921f0ddd08643a343238e9adc24578052370f6ce00bcb4286dafcb716c6e580`). Supersedes `f9d665cc...`. Same two exports.
  d3d9 unchanged (`4fdd7e04...`).
- Self-tests `[verified-numerically 2026-10-07, n=1 each]`: `pass` 6/6, `fake` 12/12 (answers 50 / 0.1), `fake ini`
  12/12 (an ini of 30 / 0.2 is read back), `flag` 12/12, `always` 12/12; d3d9 `sbs chain` passes with this nvapi.

## Suggested run (FLAT)

Same as the working run (fake, `d3d9_sbs.txt`, `r_stereo_enable 1` after loading). Expect the watch line to show
S 0.0500 and convergence 0.35, and the halves to differ: far scenery shifted about 32 px per eye at full width (16 px
in each squashed half), the gun barely. If the shift looks backwards (crossed), swap the halves or negate S; which
eye index is left was read as eye 0 → RIGHT and eye 1 → LEFT in the 2026-10-01 note, and eye 0 has sign −1 here.
