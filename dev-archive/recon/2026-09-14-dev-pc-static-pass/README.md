# 2026-09-14 — Hard Reset, dev-PC static pass (NO LAUNCH)

**Machine:** dev PC `DESKTOP-V8GTSIR`. **Install:** `D:\Program Files (x86)\Steam\steamapps\common\HardReset`,
Steam app 98400, `StateFlags=4` (fully installed) `[inferred-static 2026-09-14]` — the home PC's
2026-09-13 note flagged "installed on the home PC only, as far as this session knows"; **it is
installed here too**, so this project's `[PD]` rows can run on this machine.

**The game was not launched.** Everything here is PE headers and strings read off disk.

## Files here

| File | What it is |
| --- | --- |
| `pe-imports-hardreset.txt` | PE header + full import table for `hardreset.exe` |
| `cvar-names.txt` | 891 identifier-shaped strings, the game's console-variable vocabulary |
| `stereo-and-camera-strings.txt` | the stereo, FOV and camera strings, extracted separately |
| `squirrel-strings.txt` | evidence of the embedded scripting language |
| `install-listing.txt` | install root and `data\` contents |

## ⭐ The headline: this game already renders in stereo, and already has a console to drive it

Four console variables, sitting together, name the exact quantities a stereo renderer needs
`[inferred-static 2026-09-14]`:

```
r_stereo_enable
r_stereo_eye_separation
r_stereo_convergence
r_stereo_separation
```

and beside them, from the options-menu string table: `Stereo enable`, `Stereo eye separation`,
`Stereo convergence`, `Force stereo, need restart`, plus two gameplay hooks — `SetStereoDist` and
`SetStereoDepthCrosshair` (a crosshair that sits at the right depth is a thing only a stereo
renderer needs).

⭐ **Why this is the most valuable find of the session.** On every other project on this account the
expensive half of the work is *making the game draw the world twice, once per eye, with the right
maths*. Hard Reset appears to have shipped with that already built — the 2011-era Nvidia 3D Vision
style of stereo, driven by two numbers a console command can set.

⚠️ **Loudly unchecked, and this is the specific thing that could make it worthless:** 3D-Vision-era
stereo is often implemented **in the driver**, not the game, with the game merely passing the two
numbers through. If that is what this is, `r_stereo_enable 1` may do nothing on a modern machine and
the find evaporates. The strings prove the *controls* exist; they prove nothing about what is behind
them. `[hypothesis]`

## A real console, and a real scripting foothold

- **The console is genuine**, not a CRT artefact: the binary carries `CConsole`, a `CVar` class with
  its own AVL-tree registry, `ListenToCVar`, `Prints list of all console commands.`, and HUD-side
  cvars `r_draw_hud_console`, `s_console_lines_always_visible`, `s_console_commands_history`
  `[inferred-static 2026-09-14]`.
- **The game embeds Squirrel** — `Custom version based on Squirrel 2.2.2` — with a console command
  described as `Run external squirrel file (by default in data/scripts/debug directory).`
  `[inferred-static 2026-09-14]`.

⭐ **Read those two together.** If both hold up live, this game offers *script execution from a folder
on disk, reached through its own console* — no proxy DLL, no injector, no code patching. That is the
cheapest foothold of any project on this account, and it would mean the usual first fortnight of
reverse-engineering work simply does not apply here.

⚠️ Both are `[inferred-static]`. Debug-only commands are frequently compiled out of retail builds
while their strings remain; the string surviving is not proof the command does. **This is the single
most valuable thing to check on the first launch**, and it is one line to check it.

## 891 console variables — and the useful ones

`cvar-names.txt` holds the whole list. The ones that bear on VR work:

| Cvar | Why it matters |
| --- | --- |
| `r_fov`, `r_gameplay_fov` | field of view as a settable number, separate for gameplay |
| `r_draw_weapon`, `r_draw_hud`, `r_draw_hud_refraction` | switch off the things that break in stereo, one at a time |
| `r_show_cam_pos` | *"Show camera position coordinates"* — the camera's own numbers, on screen, free |
| `r_shader_cache_save_asm`, `r_shader_list_save` | the game will write out its own shader assembly and shader list |
| `r_win_width`, `r_win_height`, `r_win_pos_x/y`, `r_windowed_fixed_backbuffer`, `r_fullscreen` | full control of window size and placement without a config file |
| `r_render_thread` | whether rendering runs on its own thread — decides how any hook must be written |
| `r_wireframe`, `r_debug_render_mode`, `r_dump_render_lists`, `r_dump_buffers` | the game's own render debugging |
| `r_nearZ`, `r_farZ` | near/far plane, matching the menu strings `Camera near z` / `Camera far z` |

⭐ **`r_shader_cache_save_asm` deserves separate mention.** Getting a game's shader assembly normally
means a capture tool or a debugger. If this cvar does what its name says, Hard Reset will write its
own — which means the register conventions behind its camera maths are obtainable **with the game
running normally and nothing attached**.

## Binary facts

| | |
| --- | --- |
| `hardreset.exe` | **32-bit**, 7.3 MB, linked 2012-04-26 `[inferred-static 2026-09-14]` |
| Module base | `0x400000`, **ASLR off, relocations stripped** — the base never moves `[inferred-static 2026-09-14]` |
| Renderer | **Direct3D 9, confirmed from the import table**, not from strings: `d3d9.dll → Direct3DCreate9` |
| Shader reflection | `d3dx9_43.dll → D3DXGetShaderConstantTable` — the game reflects its own shaders and therefore knows its constants **by name** |
| Input | `XINPUT9_1_0.dll` (2 functions) |
| Audio / video | FMOD Ex + FMOD Event, Bink |
| Protection | `steam_api.dll` only. No wrapper section, no packer `[inferred-static 2026-09-14]` |
| Crash handling | imports `dbghelp.dll` (`StackWalk64`, `SymFromAddr`) — it symbolises its own crashes |

⭐ **The fixed module base is worth saying plainly:** every address found in this game stays valid
across runs and across sessions. Portal, by contrast, has ASLR on. That makes Hard Reset markedly
cheaper to work on than most of the estate.

⭐ **`D3DXGetShaderConstantTable` is the second-best find here.** It means the shaders carry a
constant table with real names, readable off disk. `flat-to-vr-RE-toolkit/tools/d3d9-ctab.py` exists
for exactly this, and `data\data_10_shaders.bin` is where the shaders live — **that is a piece of
`[PD]` work that needs nothing running.**

## What this does NOT establish

- Nothing here has been run. Every cvar listed is **a string in an executable**; not one has been
  typed into a console.
- How the console opens is **unknown** — no key binding was found in the strings.
- Whether `data\data_10_shaders.bin` is a readable container or a compressed archive is unchecked; it
  was listed, not opened.
- The stereo path's nature (in-game vs. driver-side) is open, and it is the question the whole
  project's cost depends on.
