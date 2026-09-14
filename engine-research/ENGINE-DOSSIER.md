# Engine Dossier — Hard Reset (Road Hog Engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `dev-archive/` and `modding-notes/` folders; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0, static recon done on both machines (2026-09-13 home, 2026-09-14 dev PC, 2026-09-14 archive + shader pass); the game has **not** been launched yet. · **VR-readiness verdict:** still one of the cheapest projects on the account, for a different reason than first thought. The stereo controls are **almost certainly NVIDIA 3D Vision** (driver-side, dead on modern hardware), but the game ships its **shaders as readable HLSL source** with the view and projection matrices uploaded **separately and by name**, a fixed module base, no protection, a real console and embedded Squirrel. All `[inferred-static]`; nothing has been run.

## 1. Identity
- Game / build / version: Hard Reset, Steam build, exe `hardreset.exe` (linked 2012-04-26, the Extended Edition era rather than the later Redux).
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC). Official release, not a fan port.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: Flying Wild Hog's own Road Hog Engine `[reported]`. Havok, FMOD, Bink and NVAPI are in use `[inferred-static 2026-09-13]`.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): Havok (physics, `hkxCamera`/`Tthkp*` symbols), FMOD Ex + FMOD Event (audio), Bink (video), NVAPI — all confirmed in the import table `[inferred-static 2026-09-14]`. **Scripting is Squirrel**: `Custom version based on Squirrel 2.2.2`, with `CSquirrelTreeWindow`, `CSquirrelValueTweaker`, `Squirrel tweakables` and a build step `..\tools\sqcompile.exe -r -i %s -o %s` visible in the strings.
- Distinctive file formats / build tags / symbol naming: **`data\*.bin` are ordinary ZIP archives with every file ZipCrypto-locked; the password is a plain string in `hardreset.exe`** — one hit among 20,830 exe strings, opening all 22 archives `[verified-numerically 2026-09-14, n=22]`. Recover it with `dev-archive/recon/2026-09-14-archive-and-shader-pass/unlock_archives.py`; the key itself is deliberately kept out of this public repo. Game scripts are compiled Squirrel under `data/scriptsbin/`.

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): **32-bit** (PE32), `hardreset.exe` 7.3 MB, linked 2012-04-26. Plain sections (`.text`, `BINK`, `.rdata`, `.data`, `.rsrc`), no protection-shaped section. ⭐ **Module base `0x400000`, ASLR OFF, relocations stripped — the base never moves** `[inferred-static 2026-09-14]`, so every address found here stays valid across runs and across sessions. (Portal, by contrast, has ASLR on.) Also imports `dbghelp.dll` (`StackWalk64`, `SymFromAddr`) — it symbolises its own crashes.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: **Direct3D 9, confirmed from the import table** (not just strings): `d3d9.dll → Direct3DCreate9` `[inferred-static 2026-09-14]`. ⭐ It also imports **`d3dx9_43.dll → D3DXGetShaderConstantTable`**, so the game reflects its own shaders and knows its constants **by name** — the `flat-to-vr-RE-toolkit/tools/d3d9-ctab.py` case exactly. `D3DCompiler_43.dll` ships beside it.
- Developer console / cvar system present? how opened?: **Yes, a real one** `[inferred-static 2026-09-14]`. The binary carries `CConsole`, a `CVar` class with its own AVL-tree registry, `ListenToCVar`, the help line `Prints list of all console commands.`, and the cvars `r_draw_hud_console`, `s_console_lines_always_visible`, `s_console_commands_history`, `s_console_show_custom_logs`. ⚠️ **How it opens is unknown** — no key binding was found in the strings. Full cvar list: `dev-archive/recon/2026-09-14-dev-pc-static-pass/cvar-names.txt` (891 names).

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: Steam API only; no wrapper or protection section found `[inferred-static 2026-09-13]`. Not tested live.
- Attach workflow that works: not yet tested.
- Injection vector that works (proxy DLL name / injector / framework): not yet tested.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)
- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**: ⭐ **shared camera constants, by name, in shipped HLSL source** (`data/shaders/common.hlsl` inside `data_10_shaders.bin`), compiled by the game at runtime (`D3DCompile` import, `r_shader_cache*` cvars) `[inferred-static 2026-09-14]`. D3D9, so these are vertex-shader float constant registers, not constant buffers.
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention: VS `c0`–`c3` `mWorldToScreen` (4x4, view × projection) · `c4`–`c6` `mWorldToCamera` (4x3, view) · `c8`–`c11` `mCameraToScreen` (4x4, projection — **shares `c8` with `vShadowBiasParams`**, so it is only meaningful in some passes) · `c15` `vVSCameraPosWS` (`w` = time) · `c16`–`c18` `mObjectToWorld` · `c29` `vHUDStereoParams`. PS `c0.w` = viewport aspect, `c51` `vPSCameraPosWS`, `c44` `vPosDecodingParams` (deferred position rebuild) `[inferred-static 2026-09-14]`. **Row-vector convention**: every use is `mul( pos, M )` `[inferred-static 2026-09-14]`. ⚠️ **Almost all world geometry goes through the combined `mWorldToScreen` directly** (`compose`, `decal`, `texture`, `shadow`, `fogVolume`, `rainBox`…); only `particle_sprites` goes view-then-projection. So a per-eye override has to rewrite **`c0`–`c3`**, not just the view at `c4`. Handedness not yet read. Table: `dev-archive/recon/2026-09-14-archive-and-shader-pass/README.md` §2.
- Where projection `P` / FOV comes from: `mCameraToScreen`; FOV as a number via `r_fov` / `r_gameplay_fov` `[inferred-static 2026-09-14]`.
- The per-eye override maths (`K_eye = …`):

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap):
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?:
- The chosen override patch point and why:

## 8. Pass inventory (by render target)
- Main scene (res/formats):
- Shadow passes (depth-only sizes):
- Post / AA chain (SMAA/TAA/motion vectors; downscale sizes):
- UI / HUD (how it's kept separate):

## 9. cvar / console cheat sheet

891 identifier-shaped names were extracted from the exe `[inferred-static 2026-09-14]`; the full list
is `dev-archive/recon/2026-09-14-dev-pc-static-pass/cvar-names.txt`. ⚠️ **Every row below is a string
in an executable. Not one has been typed into a console.** The prefixes are `r_` render (173),
`s_` settings (51), `g_` game (41), `p_` physics (15), `e_` editor (10), plus large `UI_` and `HK`
(Havok) groups.

| command / cvar | effect (from the game's own menu text where quoted) | use |
|---|---|---|
| `r_stereo_enable` | "Stereo enable" | master switch for **NVIDIA 3D Vision via NVAPI**, almost certainly — see §11 `[inferred-static 2026-09-14]`. (The "Force stereo, need restart" text is the audio option `s_sound_forcestereo` — its reading as a render setting is `[disproved 2026-09-14]`.) |
| `r_stereo_eye_separation` | "Stereo eye separation" | 3D Vision separation, passed to the driver `[inferred-static 2026-09-14]` |
| `r_stereo_convergence` | "Stereo convergence" | 3D Vision convergence `[inferred-static 2026-09-14]` |
| `r_stereo_separation` | — | a second separation knob; relationship to the above unknown |
| `SetStereoDist`, `SetStereoDepthCrosshair` | script-side stereo helpers | a crosshair at correct depth is a stereo-only need |
| `r_fov`, `r_gameplay_fov` | field of view, gameplay FOV separately | FOV as a number |
| `r_nearZ`, `r_farZ` | "Camera near z" / "Camera far z" | near-plane work |
| `r_show_cam_pos` | "Show camera position coordinates" | the camera's numbers on screen, free |
| `r_draw_weapon`, `r_draw_hud`, `r_draw_hud_refraction` | draw toggles | switch off what breaks in stereo, one at a time |
| `r_shader_cache_save_asm`, `r_shader_list_save` | write out shader assembly / shader list | ⭐ shader register conventions with **nothing attached** |
| `r_render_thread` | rendering on its own thread | decides how any hook must be written |
| `r_win_width`, `r_win_height`, `r_win_pos_x/y`, `r_windowed_fixed_backbuffer`, `r_fullscreen` | window control | windowed test runs without editing a config |
| `r_wireframe`, `r_debug_render_mode`, `r_dump_render_lists`, `r_dump_buffers` | the game's own render debugging | pass inventory for free |
| (Squirrel) | "Run external squirrel file (by default in data/scripts/debug directory)." | ⭐ **script execution from a folder, no injection** — if it survived into the retail build |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used):
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- **The "built-in stereo renderer" is very probably NVIDIA 3D Vision, not the game's own doubling** `[inferred-static 2026-09-14]`. Evidence: the exe imports `nvapi.dll` / `nvapi_QueryInterface` (how a game sets 3D Vision separation and convergence); and across ~40 shipped HLSL sources the **only** per-eye code is `vHUDStereoParams.x` added to x position in the three HUD/text shaders (`font`, `font_out`, `animatix`) — no world shader does anything per eye. That is the 3D Vision pattern: driver doubles the world, the game places its own HUD at a depth. NVIDIA dropped 3D Vision in 2019, so expect `r_stereo_enable 1` to do nothing. **Still possible:** CPU-side doubling with two `mWorldToCamera` uploads that no shader would show. Separating observation: one flat launch with `r_stereo_enable 1`. Supersedes the §12 hope recorded earlier the same day.
- "Force stereo, need restart" is **audio** (`s_sound_forcestereo`), not a render option `[disproved 2026-09-14]`.

## 12. Open risks toward the North Star
- Nothing blocking seen yet. A small, unprotected 32-bit Direct3D 9 exe with a fixed module base is the friendliest starting point of this batch.
- ~~The game appears to ship its own stereo renderer~~ — **probably not**: the controls drive NVIDIA 3D Vision (§11) `[inferred-static 2026-09-14]`. One flat launch confirms.
- ⭐ **What replaces that hope:** shaders are compiled at runtime from shipped HLSL source, with view and projection uploaded separately by name (§6). **Open question worth a flat run: will the game compile a loose, edited `data\shaders\*.hlsl` from disk in preference to the archive copy** (with `r_shader_cache 0`)? If yes, a first per-eye camera test needs no injected code at all `[hypothesis]`. If no, the archive can be rebuilt with the recovered key, or the constants set from a D3D9 hook at the known slots.
- The HUD already knows how to be pushed to a per-eye depth (`vHUDStereoParams`) — useful later for a readable VR HUD `[inferred-static 2026-09-14]`.
- ⚠️ **Debug-only console commands are routinely compiled out of retail builds while their strings survive.** That applies to the Squirrel run-a-file command and to much of the `r_show_*` family. A string is not a command.
- **Nothing has been run.** The whole entry above is static reading.
