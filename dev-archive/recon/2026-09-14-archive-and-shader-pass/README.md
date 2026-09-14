# 2026-09-14 — archive and shader pass (dev PC `DESKTOP-V8GTSIR`, no launch)

Closes the one `[PD]` row on the board: *open `data\data_10_shaders.bin` and see whether the
shaders are readable off disk.* They are — far more readable than the row hoped for.
Nothing was run. No game file is committed here; extracted content stayed in a local scratch folder.

## 1. The data archives are password-locked ZIPs, and the password is in the exe

- All 22 `data\*.bin` files are standard ZIP archives (`PK\x03\x04`). Every non-directory entry is
  **ZipCrypto-encrypted** (deflate inside) `[measured 2026-09-14]`.
- The password is a **plain 28-character string inside `hardreset.exe`**. Trying every printable
  string in the exe (20,830 candidates) against the smallest locked entry gave **exactly one hit**,
  and that key then opened an entry in **all 22 archives, 0 failures** `[verified-numerically 2026-09-14, n=22]`.
  Python's `zipfile` checks the CRC, so the hit is a real unlock, not the 1-in-256 header-byte fluke.
- `unlock_archives.py` (this folder) repeats that on anyone's own install. **It never prints the key
  and the key is deliberately not written into this public repo** — it would hand out the game's
  asset lock to people who don't own the game, and anyone who does can recover it in seconds.

## 2. ⭐ The shaders ship as HLSL SOURCE, and the game compiles them itself

`data_10_shaders.bin` holds 66 entries: `default_cache.bin` (7.0 MB compiled cache, version file
`2012-01-31`), **~40 `.hlsl` source files** (`common.hlsl`, `opaque.hlsl`, `deferredLight.hlsl`,
`water.hlsl`, the `pp*` post chain, `fxaa.hlsl` + NVIDIA `Fxaa3_11.h`), their `.cfg` sampler files, and
a handful of fixed-function-style `.vs`/`.ps` files that are fxc output listings `[measured 2026-09-14]`.

The exe imports `D3DCompile` and carries `r_shader_cache`, `r_shader_cache_preload`,
`r_shader_cache_save_asm` and `data\default_cache.bin` `[inferred-static 2026-09-14]`: the engine
compiles this source at runtime and caches the result. **So the camera maths is not something to
recover by disassembly — it is written down, with names and register slots.**

Vertex-shader constant slots from `common.hlsl` (names and slots only — interface, not content):

| slot | name | what it is |
|---|---|---|
| `c0`–`c3` | `mWorldToScreen` (4x4) | ⭐ the full world → screen transform (view × projection) |
| `c4`–`c6` | `mWorldToCamera` (4x3) | ⭐ the view matrix on its own |
| `c8`–`c11` | `mCameraToScreen` (4x4) | ⭐ the projection on its own — **shares `c8` with `vShadowBiasParams`**, so it is only valid in some passes |
| `c15` | `vVSCameraPosWS` | camera position in world space, `w` = time |
| `c16`–`c18` | `mObjectToWorld` (4x3) | per-object world matrix |
| `c28`+ | `mSkinning[76]` | skinning palette (shares `c28` with `vPPAnimatixUV`) |
| `c29` | `vHUDStereoParams` | ⭐ see §3 |

Pixel side: `vAmbientColor.w` = viewport aspect ratio (`c0`), `vPSCameraPosWS` (`c51`),
`vRenderTargetScale/Offset` (`c42`/`c43`), `vPosDecodingParams` (`c44`, depth → position reconstruction
for the deferred lighting).

View and projection reaching the GPU **separately and by name** is a good layout for a VR camera
`[inferred-static 2026-09-14]`. Two details read from the shader bodies:

- **Row vectors:** every use is `mul( pos, M )`.
- ⚠️ **Nearly all world geometry uses the combined `mWorldToScreen` directly** (`compose`, `decal`,
  `texture`, `shadow`, `fogVolume`, `rainBox`, `flare`, `lightning`); only `particle_sprites` goes
  `mWorldToCamera` then `mCameraToScreen`. So a per-eye camera must rewrite **`c0`–`c3`**, not only the
  view at `c4` — the separate view and projection are the ingredients to compute that product from.

## 3. ⚠️ The built-in "stereo renderer" is almost certainly NVIDIA 3D Vision, not the game's own

This answers the question the 2026-09-14 static pass left open — **statically, not live**:

- The exe imports **`nvapi.dll` / `nvapi_QueryInterface`** — how a game drives NVIDIA 3D Vision
  (separation and convergence are set through NVAPI; the driver does the actual doubling)
  `[inferred-static 2026-09-14]`.
- In ~40 shader sources the **only** stereo code is `vHUDStereoParams.x`, added to the x position in
  **three HUD/text shaders** (`font`, `font_out`, `animatix`). **No world shader does anything per
  eye** `[measured 2026-09-14]`. That is exactly the 3D Vision pattern: the driver shifts the world, and
  the game pushes its own HUD to a chosen depth so it doesn't sit at the screen plane.
- **Correction:** the menu text "Force stereo, need restart" belongs to the **audio** setting
  `s_sound_forcestereo` (it sits between `s_sound_dopplerratio` and "Force mono, need restart"), not to
  `r_stereo_enable`. The 2026-09-14 static pass read it as a render option `[disproved 2026-09-14]`.

**What would still change this:** the world could be doubled on the CPU side (two views, two
`mWorldToCamera` uploads) without any shader knowing. Nothing in the source points that way, but the
separating observation is live: set `r_stereo_enable 1` on a non-3D-Vision machine and see whether the
frame is drawn twice. Expectation now: **nothing happens** `[hypothesis]`.

## 4. What this changes

The "free stereo renderer" hope is probably gone. In its place is something cheaper to build on than
most of the estate: named, separated view and projection matrices in readable shader source, a fixed
module base, no protection, and a HUD that already knows how to be pushed to a depth per eye.

The new question worth a flat run: **will the game compile a loose, edited `.hlsl` from disk instead
of the archive copy** (with `r_shader_cache 0` so the cache doesn't win)? If it does, a first stereo
test needs no injected code at all.
