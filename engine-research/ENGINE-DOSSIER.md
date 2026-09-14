# Engine Dossier — Hard Reset (Road Hog Engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `dev-archive/` and `modding-notes/` folders; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0, static recon done on both machines (2026-09-13 home, 2026-09-14 dev PC); the game has **not** been launched yet. · **VR-readiness verdict:** potentially the cheapest project on the account — the game ships **its own stereo renderer controls**, a real console, and an embedded scripting language with a run-a-file-from-disk command. Every part of that is `[inferred-static]` and one launch decides whether any of it is live.

## 1. Identity
- Game / build / version: Hard Reset, Steam build, exe `hardreset.exe` (linked 2012-04-26, the Extended Edition era rather than the later Redux).
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC). Official release, not a fan port.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: Flying Wild Hog's own Road Hog Engine `[reported]`. Havok, FMOD, Bink and NVAPI are in use `[inferred-static 2026-09-13]`.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): Havok (physics, `hkxCamera`/`Tthkp*` symbols), FMOD Ex + FMOD Event (audio), Bink (video), NVAPI — all confirmed in the import table `[inferred-static 2026-09-14]`. **Scripting is Squirrel**: `Custom version based on Squirrel 2.2.2`, with `CSquirrelTreeWindow`, `CSquirrelValueTweaker`, `Squirrel tweakables` and a build step `..\tools\sqcompile.exe -r -i %s -o %s` visible in the strings.
- Distinctive file formats / build tags / symbol naming: Data under `data\`, not yet looked at.

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
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention:
- Where projection `P` / FOV comes from:
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
| `r_stereo_enable` | "Stereo enable"; menu also shows "Force stereo, need restart" | ⭐ the stereo renderer's master switch |
| `r_stereo_eye_separation` | "Stereo eye separation" | ⭐ interpupillary distance |
| `r_stereo_convergence` | "Stereo convergence" | ⭐ where the eyes converge |
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
- none yet.

## 12. Open risks toward the North Star
- Nothing blocking seen yet. A small, unprotected 32-bit Direct3D 9 exe with a fixed module base is the friendliest starting point of this batch.
- ⭐ **The game appears to ship its own stereo renderer** (`r_stereo_enable` / `_eye_separation` / `_convergence`, plus menu text and script helpers) `[inferred-static 2026-09-14]`. On every other project here the expensive half is making the game draw the world twice with the right maths; this one may have that already.
- ⚠️ **The specific way that find could be worthless:** 2011-era stereo is often implemented **in the graphics driver** (3D Vision), with the game only passing the two numbers through. If so, `r_stereo_enable 1` may do nothing on a modern machine. The strings prove the *controls* exist and prove nothing about what is behind them `[hypothesis]`.
- ⚠️ **Debug-only console commands are routinely compiled out of retail builds while their strings survive.** That applies to the Squirrel run-a-file command and to much of the `r_show_*` family. A string is not a command.
- **Nothing has been run.** The whole entry above is static reading.
