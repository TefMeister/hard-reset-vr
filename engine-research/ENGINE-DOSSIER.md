# Engine Dossier — Hard Reset (Road Hog Engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `dev-archive/` and `modding-notes/` folders; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0, static recon done on both machines (2026-09-13 home, 2026-09-14 dev PC, 2026-09-14 archive + shader pass); **first launch 2026-09-14** (`/ms`, dev PC): console works, `r_stereo_enable` is live, loose-shader test set up but not yet run (`modding-notes/2026-09-14-first-launch-console-and-stereo.md`). · **VR-readiness verdict:** still one of the cheapest projects on the account, for a different reason than first thought. The stereo controls are **almost certainly NVIDIA 3D Vision** (driver-side, dead on modern hardware), but the game ships its **shaders as readable HLSL source** with the view and projection matrices uploaded **separately and by name**, a fixed module base, no protection, a real console and embedded Squirrel. Mostly `[inferred-static]`; see §9 and §11 for what the first launch confirmed and overturned.

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
- Developer console / cvar system present? how opened?: **Yes, a real one** `[inferred-static 2026-09-14]`. The binary carries `CConsole`, a `CVar` class with its own AVL-tree registry, `ListenToCVar`, the help line `Prints list of all console commands.`, and the cvars `r_draw_hud_console`, `s_console_lines_always_visible`, `s_console_commands_history`, `s_console_show_custom_logs`. **Opens with Ctrl + ~** in the retail build `[verified-live 2026-09-14, n=1]` (the shipped patch notes' "console commands removed" line is out of date). Typed commands persist in the profile `config.cfg` as `s_console_commands_history`. Some cvars are start-up only and answer "read only" (`r_shader_cache`) `[verified-live 2026-09-14, n=1]`. **User state:** `Documents\Hard Reset Extended\profiles\<name>\config.cfg` (`name "value"`, CRLF), `binds.cfg`, saves; shader cache copied to `Documents\Hard Reset Extended\cache\cache.bin` `[measured 2026-09-14]`. Full cvar list: `dev-archive/recon/2026-09-14-dev-pc-static-pass/cvar-names.txt` (891 names).

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
is `dev-archive/recon/2026-09-14-dev-pc-static-pass/cvar-names.txt`. ⚠️ **Rows are strings in an executable unless marked live.** Typed so far (2026-09-14):
`_version`, `r_stereo_enable`, `r_stereo_eye_separation`, `r_shader_cache`. The prefixes are `r_` render (173),
`s_` settings (51), `g_` game (41), `p_` physics (15), `e_` editor (10), plus large `UI_` and `HK`
(Havok) groups.

| command / cvar | effect (from the game's own menu text where quoted) | use |
|---|---|---|
| `r_stereo_enable` | "Stereo enable" | **Live, no restart:** `1` blows the picture out to white/magenta with a quarter-size foreign buffer in the top-left corner; `0` restores it `[verified-live 2026-09-14, n=3 cycles]`. Built for **NVIDIA 3D Vision via NVAPI** `[inferred-static 2026-09-14]` — see §11. (The "Force stereo, need restart" text is the audio option `s_sound_forcestereo` — its reading as a render setting is `[disproved 2026-09-14]`.) |
| `r_stereo_eye_separation` | "Stereo eye separation" | 3D Vision separation `[inferred-static 2026-09-14]`. 0 vs 5 with stereo on: no visible difference, eyeballed `[verified-live 2026-09-14, n=1]` |
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

## Inbox folds, 2026-10-08 (`/lm`, dev PC)

Folded and deleted: `2026-10-07-gr-steamvr-has-a-32-bit-openxr-runtime.md`, `2026-10-08-pd-nvapi-stand-in-eye-labels.md`.

- **Home-PC runtime:** SteamVR 2.17+ (stable 2026-09-10) ships a 32-bit OpenXR runtime, `...\SteamVR\steamxr_win32.json`,
  so `runtime_json=` can point there on the home PC; Virtual Desktop's VDXR is the fallback `[reported]`. Not tried on
  our machines. Source: `external-research/topics/2026-10-07-steamvr-2-17-ships-a-32-bit-openxr-runtime.md`.
- **nvapi stand-in log labels:** `staging/hard-reset-vr/proxy-nvapi/src/nvapi_proxy.c` still has `EYE_LEFT 1`,
  `EYE_RIGHT 2`; NVIDIA's `NV_StereoActiveEye` is RIGHT = 1, LEFT = 2 `[reported]`. Only the stand-in's own log names
  are crossed; pictures are right (the d3d9 proxy passes the raw number through). Swap the two defines when next built.

## ⭐ 2026-10-08 (`/lm`): ONE UNIT IS A METRE; HEAD POSITION WORKS IN THE SIMULATOR

Note `modding-notes/2026-10-08-lm-units-are-metres-and-head-position-works.md`; evidence `dev-archive/recon/2026-10-08-units-and-hud/`.

- **World z is up**; `camera at` in the log is a world position `[verified-live 2026-10-08, n=3 walks]`.
- **Units = metres:** walk ~7 units/s live vs the player template's Speed 6.6; capsule height 2.0, radius 0.5,
  eye 1.65 above the feet (`scriptsbin/main/gameSystem/player/user.nut` CAMERA_POS; `.../base_templates/player/player.nut`),
  Jump 6.6, no crouch `[inferred-static 2026-10-08]` + `[verified-live 2026-10-08, n=3]`. Scripts are compiled
  Squirrel; the reader's disassembler is not in a repo yet.
- **`[xr] units_per_metre=1.0`, `head_position=1`** (read at start-up): sideways and forward head moves give
  correct parallax on the held gun; back to 0 restores exactly `[verified-live 2026-10-08, n=1 each]`; maths
  checked numerically, no bug `[verified-numerically 2026-10-08, n=1]`. Gap: the game's own eye position
  (lighting/fog constants c15/c51) is not moved `[inferred-static 2026-10-08]`.
- **The HUD dial is a 3D object on the gun**, not a flat overlay: it shows head parallax like the gun, and
  the panel test (`d3d9_hud.txt`) placed only ~1 draw per frame with no visible change `[verified-live 2026-10-08, n=1]`.
  The orthographic-HUD idea is wrong for the dial `[disproved 2026-10-08]`; it may still hold for text.

## 2026-10-08 evening (`/lm`): THE HUD PANEL LIVE, PARTLY

Note `modding-notes/2026-10-08-lm-the-panel-takes-the-menu-but-not-its-frames.md`. With `d3d9_hud.txt` on and stereo
on, the pause menu's words and fills land on the panel exactly where a screen 2 m ahead belongs in each eye (centre x
402 / 237 against 402 / 238 by the lens maths, 640 px per eye) `[measured 2026-10-08, n=1]`; placed 2,100/s in the
menu, ~550/s in gameplay. The menu's outline frames are NOT placed: same image position in both eyes (wrong depth,
divergent) `[measured 2026-10-08, n=1]`. Panel off: the menu is whole again. Next: find the frame-line shader.

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used): `steam://run/98400` → Escape/Enter through the films → the main menu
  answers absolute mouse clicks ("Resume game" at client 636,288 in 1280x720) → ~70 s of loading and comic panels →
  any key (Space) → gameplay `[verified-live 2026-10-07, n=1]`; about 4 Enters at the intro (more opens NEW GAME → New campaign). Console: Ctrl+~, then type (SendInput unicode). Stereo: `r_stereo_enable 1` every launch. Close: console `quit` `[verified-live 2026-10-08, n=2]`.
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- **The "built-in stereo renderer" is very probably NVIDIA 3D Vision, not the game's own doubling** `[inferred-static 2026-09-14]`. Evidence: the exe loads `nvapi.dll` / `nvapi_QueryInterface` (⚠️ by `LoadLibrary` at run time, `0x6bd0c0`, not the import table — corrected 2026-10-01) (how a game sets 3D Vision separation and convergence); and across ~40 shipped HLSL sources the **only** per-eye code is `vHUDStereoParams.x` added to x position in the three HUD/text shaders (`font`, `font_out`, `animatix`) — no world shader does anything per eye. That is the 3D Vision pattern: driver doubles the world, the game places its own HUD at a depth. ~~NVIDIA dropped 3D Vision in 2019, so expect `r_stereo_enable 1` to do nothing~~ — **that prediction was wrong** `[disproved 2026-09-14]`: it visibly changes rendering (§9). What it does looks like a render-target mix-up (wrong buffer composed, a buffer shown in a corner), and eye separation 0 vs 5 changed nothing visible, so **game-side doubling is still unshown** `[hypothesis]`. Patch 1.2 notes: "Full Nvidia 3dVision support" `[reported]`. **Separating step, no game needed:** follow the `r_stereo_enable` cvar in the exe (fixed base `0x400000`) and read what it switches — render targets, NVAPI calls, or a second camera upload. Supersedes the §12 hope recorded earlier the same day.
- "Force stereo, need restart" is **audio** (`s_sound_forcestereo`), not a render option `[disproved 2026-09-14]`.

## 12. Open risks toward the North Star
- Nothing blocking seen yet. A small, unprotected 32-bit Direct3D 9 exe with a fixed module base is the friendliest starting point of this batch.
- ~~The game appears to ship its own stereo renderer~~ — **probably not**: the controls drive NVIDIA 3D Vision (§11) `[inferred-static 2026-09-14]`. One flat launch confirms.
- ⭐ **What replaces that hope:** shaders are compiled at runtime from shipped HLSL source, with view and projection uploaded separately by name (§6). **Open question worth a flat run: will the game compile a loose, edited `data\shaders\*.hlsl` from disk in preference to the archive copy** (with `r_shader_cache 0`)? If yes, a first per-eye camera test needs no injected code at all `[hypothesis]`. If no, the archive can be rebuilt with the recovered key, or the constants set from a D3D9 hook at the known slots.
- The HUD already knows how to be pushed to a per-eye depth (`vHUDStereoParams`) — useful later for a readable VR HUD `[inferred-static 2026-09-14]`.
- ⚠️ **Debug-only console commands are routinely compiled out of retail builds while their strings survive.** That applies to the Squirrel run-a-file command and to much of the `r_show_*` family. A string is not a command.
- **Nothing has been run.** The whole entry above is static reading.

## Inbox folds, 2026-09-29

**⭐ 2026-10-01 (`/pd`): THE GAME'S OWN TWO-EYE LOOP, TRACED** `[inferred-static 2026-10-01]`. Start-up `0x973694`:
NvAPI Initialize → `SetDriverMode(2)` (direct) → IsEnabled/Enable. Every frame `0x973700`: eye count `[0xdccfe8]` =
1 + (cvar byte `[eax+0xdcc134]` ≠ 0, very probably `r_stereo_enable`); driver stereo is activated (`0x9731a0`) only if
the driver reports it enabled and `[0xbc1bb8] == 120`. The eye loop (`0x976336`, `0x8a6b60` per eye) runs from the
cvar alone; before each eye `SetActiveEye(handle, idx 0 → 2, 1 → 1)` (`0x976d4f`, `0x96b036`); per-eye ± constant at
`0x96f14b` = `vHUDStereoParams` (c29.x = −1 / +1): the game shifts only the **HUD** per eye; the world shift was the
driver's. This explains the 2026-09-14 blown-out picture (both eyes into one screen). **VR route:** a stand-in
`nvapi.dll` beside the exe (the game `LoadLibrary`s it by name) that reports stereo on and uses `SetActiveEye` as the
per-eye signal to switch render target and projection `[hypothesis]`. Note
`modding-notes/2026-10-01-pd-the-game-draws-two-eyes-from-a-console-setting.md`.

**Hard Reset is listed as a 3D Vision DIRECT MODE game (`/gr` 2026-09-29).** wiz3D lists it among games that render both eyes themselves and choose the eye with `SetActiveEye`; its maintainer reports it working after a September 2026 fix, in which the game's start-up `Stereo_Deactivate` is a handshake, not an off-switch `[reported]`. §11's "no per-eye code in any world shader" is also what Direct Mode looks like, and the 2026-09-14 live result fits "the stereo path started but the driver never said stereo was active" `[hypothesis]`. Separating step, static: find the NVAPI stereo call order in the exe (Deactivate → IsActivated → Activate → SetActiveEye per frame); if present, a logging `nvapi.dll` of our own that answers "active" is the lever. Topic: `external-research/topics/2026-09-29-hard-reset-is-a-3d-vision-direct-mode-game.md`.


## Inbox folds and live results, 2026-10-07 (`/lm`, dev PC)

Folded and deleted: `2026-10-04-gr-fake-stereo-answers-not-activated.md`, `2026-10-07-pd-fake-stereo-flag.md`.
Evidence: `dev-archive/recon/2026-10-07-two-eyes-and-loose-shaders/`.

- ⭐⭐⭐ **The game draws both eyes itself** `[verified-live 2026-10-07, n=1]`: `r_stereo_enable 1` from the console,
  our nvapi.dll in PASS-THROUGH: SetActiveEye LEFT/RIGHT ~119/s each, mono 0. So the eye loop runs on this PC's real
  driver (it answers IsActivated with status -140 but activated=1); `/gr`'s worry that a "not activated" answer stops
  it did not arise here. **But the window stops updating** in stereo mode (last frame frozen, the game keeps running):
  the eye pictures are not reaching the window. Next: a d3d9 proxy that captures each eye (reader building it).
- ⭐⭐ **Loose shaders are compiled** `[verified-live 2026-10-07, n=1]`: `data\shaders\<name>.hlsl` plus
  `r_shader_cache "0"` replaced the shipped tone-mapping shader (the world turned red, the HUD did not). A
  no-injection route for per-eye shader edits.
- How the game decides on driver stereo (function `0x9731a0`) `[inferred-static 2026-10-07]`: it forces "want" off
  unless [0xbc1daa] ≠ 0, [0xbc1bec] ≠ 0 and the DWORD [0xbc1bb8] == 120; then Activate/Deactivate if the answer
  differs; an IsActivated "no" does not stop the eye loop there.
- Fake mode now remembers Activate (ignores a Deactivate before the first Activate; `nvapi_fake_always_activated.txt`
  forces yes), and a read-only watch logs [0xbc1bb8] once a second: staging `15efcc6`, `cfd70f900faf`
  `[compile-verified 2026-10-07]`, not installed (pass-through was enough).

## ⭐⭐⭐ 2026-10-07 (later, `/lm`): STEREO SIDE BY SIDE IN THE WINDOW, WITH REAL DEPTH

Folded and deleted: inbox `2026-10-07-pd-eye-capture-proxy.md`, `-stereo-clear-fails.md`, `-stereo-gates.md`,
`-separation.md`. Evidence: `dev-archive/recon/2026-10-07-side-by-side-first-light/`.

- **Working recipe** `[verified-live 2026-10-07, n=1]`: our `nvapi.dll` (`1921f0ddd086`) in FAKE mode
  (`nvapi_fake_stereo.txt`) + our `d3d9.dll` (`4fdd7e04b0b4`) with `d3d9_sbs.txt`; load in, then type
  `r_stereo_enable 1` (the game resets it at device set-up). The window shows left | right, 60 fps, HUD in both,
  far scenery 32 px apart, the gun ~3 px `[measured 2026-10-07]`. Halves possibly swapped (eye 0 is RIGHT)
  `[hypothesis]`. Menus are doubled too while it is on (clicks must go to the left half, or switch sbs off).
- **Three gates** `[inferred-static 2026-10-07]`, each confirmed by a live run:
  (A) [0xbc1daa] "driver says stereo is enabled", set at start-up only after SetDriverMode(DIRECT) succeeds; without
  it the second eye's surfaces are never built and every eye-1 Clear fails (D3DERR_INVALIDCALL), frames smear.
  (B) [0xbc1bec] = `r_fullscreen`, (C) [0xbc1bb8] = the `r_fullscreen_refreshes` number, must be 120. Every frame
  `0x9731a0` asks IsActivated; if that SUCCEEDS the game forces its wish off unless A, B and C pass and writes it back
  into `r_stereo_enable` (→ one eye when windowed). So fake mode answers IsActivated with an error (-140), and the
  console setting alone keeps both eyes.
- **Eye shift is the game's own** (supersedes the 2026-10-01 note that it was the driver's job): per eye,
  clip.x += sign·S·(w − convergence), S = `r_stereo_separation` × `r_stereo_eye_separation`, taken at device set-up
  from GetSeparation×0.01 and GetEyeSeparation; convergence is the game's own `r_stereo_convergence` (0.35). Our
  fake answers 50 % and 0.1 (settable in `nvapi_stereo.ini`).
- **d3d9 capture**: at each SetActiveEye (handed over from our nvapi), the back buffer is copied into that eye's half
  of a double-width surface; at Present it is stretched back over the back buffer. Switch files are re-read each
  second.
- UAC at every launch: Steam re-runs the DirectX installer (`HKLM\SOFTWARE\WOW6432Node\Valve\Steam\Apps\98400` has
  `vcredist` but no `directx`).

## 🏆 2026-10-07 (evening, `/lm`): IN THE OPENXR HEADSET SIMULATOR

Folded and deleted: inbox `2026-10-07-pd-openxr-bridge.md`. Evidence: `dev-archive/recon/2026-10-07-in-the-headset-simulator/`.

- **Eye numbers** (supersedes "eye 0 is RIGHT"): NVAPI's `NV_StereoActiveEye` is RIGHT = 1, LEFT = 2 `[reported]`; our
  proxies had them backwards. Fixed in d3d9 `ae49c7b1b487`; live, far scenery now sits 32 px further left in the left
  half `[measured 2026-10-07]`. `d3d9_swap_eyes.txt` crosses them if ever needed. (The nvapi log still prints the old
  names; behaviour is right.)
- **OpenXR bridge in the d3d9 proxy** `[verified-live 2026-10-07, n=1]`: `d3d9_openxr.txt` on, `d3d9_vr.ini`
  `runtime_json=` (32-bit runtime; the dev PC uses `openxr_simulator-32.json`), 32-bit `openxr_loader.dll`
  `fb1e06de9653` beside the exe. Own D3D11 device + session on a headset thread, projection layers. Handover by CPU:
  each Present copies the two-eye surface into a ring of 3 GPU copies, reads the oldest finished one back
  (GetRenderTargetData) into a 3-slot CPU frame; the headset thread uploads it. Live: ~14 ms per readback, ~40 new
  frames/s reach the headset, 60 headset frames/s submitted. Speeding this up is the next job.
- The game pauses itself when its window loses focus.
- **Hand-over speed** `[verified-live 2026-10-07, n=1]` (folded from inbox `2026-10-07-pd-faster-handover.md`, which
  supersedes "the WAIT readback is never waited for"): the 14 ms was LockRect waiting for GetRenderTargetData's queued
  copy. ASYNC readback (own system-memory surface per ring slot, locked only after its event query lands;
  `d3d9_readback_async.txt`) costs 1.1 ms and hands over every frame. The game creates 18 MANAGED textures, so D3D9Ex
  would need them re-pooled.

## 🏆 2026-10-07 (late, `/lm`): HEAD TRACKING AND THE HEADSET'S LENS, IN THE SIMULATOR

Folded and deleted: inbox `2026-10-07-pd-headset-fov-and-tracking.md`. Evidence: `dev-archive/recon/2026-10-07-head-tracking-simulator/`.

- **Camera** `[inferred-static 2026-10-07]`: class vtable `0xa8df64`; slot 25 `0x9a9770` per-frame update writes fov
  `+0x2c`, near/far `+0x34/+0x38`, view `+0x40` (fresh from the scene node each frame), eye-0/eye-1/mono projections
  `+0x200/+0x240/+0x280`, products `+0x2c0..`, inverses `+0x80..`/`+0x140..`; slot 26 `0x9a9dd0` publishes into the
  render frame at `0xdcbec0 + 0x560·([0xdcca58]^[0xdcca60])`. Row vectors, right-handed, −z forward = OpenXR's frame.
- **Our wrap of slots 25/26** (vtable patch, checks the exe first) `[verified-live 2026-10-07, n=1]`: headset lens per
  eye (replaces the game's own S/convergence shift), wider culling lens, head rotation into the view before culling,
  pose carried with each picture to the headset layer. Yaw/pitch/roll all follow; the horizon stays level in the
  headset. Head position off until units per metre is measured (camera position is logged).

## 2026-10-07 (`/pd`): THE HUD ON A PANEL AT A SET DISTANCE (built, not yet run in the game)

- Only `font`, `font_out` and `animatix` are per eye: `clip = pos * mWorldToScreen (c0..c3)`, then `clip.x +=
  vHUDStereoParams.x (c29) * factor` `[inferred-static 2026-10-07]` (shader sources). The device is PURE (`0x454`), so
  no constant can be read back; our stand-in copies them as they are set.
- `d3d9_hud.txt` (d3d9 `172eb78aa4ca`, staging `972fcee`): HUD-shader draws with an orthographic `c0..c3` get
  `mWorldToScreen * A_eye`, `c29.x = 0`; `A_eye` puts the screen on a panel `hud_distance_m` ahead (2.0),
  `hud_width_deg` wide (50), through each eye's lens, depth pinned in front of everything `[verified-numerically
  2026-10-07, n=1]` (simulator device test, within 2 px). The game's own packing ("by columns" expected) and its
  HUD matrix being orthographic are `[hypothesis]` until the `hud per s` log line, live. Note
  `modding-notes/2026-10-07-pd-hud-on-a-panel.md`.

## The HUD is 3D on purpose (2026-10-08, `/pd`, static)

`[inferred-static 2026-10-08]`: the HUD item `data/items/hud/hud.rhs` (script `base_templates/item/hud.nut`) spawns two
animatix screens attached to the player: `animatix_hud_3d_stats` at `arm02_attachment` (radar, health, shield, ammo)
and `animatix_hud_3d_bars` at `main_attachment` (bars). They draw in world space, already correct in stereo; leave
them. The flat `animatix_hud_2d` template is referenced by nothing. Screen-space draws are crosshairs, damage
indicators, blood, menus, loading and briefing: those are what the panel (`d3d9_hud.txt`) is for. Note
`modding-notes/2026-10-08-pd-the-hud-is-built-in-3d.md`.
