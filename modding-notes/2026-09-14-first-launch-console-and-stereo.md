# 2026-09-14 — first launch: the console works, the stereo switch does something, shader test half-done

**Machine:** dev PC `DESKTOP-V8GTSIR` (GTX 1660 SUPER, driver 32.0.15.6094), windowed 1280x720.
**Lane:** `/ms` — Tefa at the keyboard, Claude reading screenshots and files. First time the game
has been run for this project.

## What was established

- **The console opens with Ctrl + ~** in the retail 1.51 Steam build `[verified-live 2026-09-14, n=1]`.
  The shipped `patch_notes.txt` says console commands were removed "for the time being"; that is out of
  date. Typed commands are saved between runs in the profile's `config.cfg` as
  `s_console_commands_history` — a free record of exactly what was typed, typos included.
- **Where the game keeps its state:** `Documents\Hard Reset Extended\` → `profiles.cfg`,
  `profiles\<name>\config.cfg` (cvars as `name "value"`, CRLF) + `binds.cfg` + saves, and
  `cache\cache.bin` (+ `.ver`), a byte-identical copy of the shipped `data/default_cache.bin`
  `[measured 2026-09-14]`.
- **`r_stereo_enable 1` changes rendering live, with no restart** `[verified-live 2026-09-14, n=3 on/off cycles]`:
  the picture blows out to overexposed white and magenta, and a quarter-size image of a different
  buffer (dark, glowing particles) appears in the top-left corner. `r_stereo_enable 0` restores it
  at once. Screenshots: Tefa's `Pictures\Screenshots\Screenshot (245).png` (menu, on), `(246)` (off),
  `(249)` (gameplay, on).
- **`r_stereo_eye_separation` at 0 and at 5 made no difference Tefa could see** with stereo on
  `[verified-live 2026-09-14, n=1]`. Eyeballed, not measured — a small sideways shift inside a blown-out
  picture could be missed.
- **`r_shader_cache` is read-only from the console** ("read only") `[verified-live 2026-09-14, n=1]`, so
  it can only be set before start-up.
- The game runs on the NVIDIA card, not the Intel one (`nvidia-smi` process list) `[measured 2026-09-14]`.

## What is NOT established

- **Whether the game draws two views.** The static prediction was "`r_stereo_enable 1` does nothing";
  it does something, so that prediction was wrong. But what it does looks like a **render-target
  mix-up** in the 3D Vision path — a wrong buffer composed at the wrong scale, plus a buffer shown in
  a corner — not like doubling, and the separation value did nothing visible `[hypothesis]`.
  Eyeballing cannot settle this; reading what `r_stereo_enable` switches in the exe can, and needs no
  game running.
- **Whether the game compiles a loose, edited shader.** Test set up but not run (see below).
- Squirrel run-a-file: not tried.

## ⚠️ State left on the machine on purpose (the shader test is mid-way)

1. `D:\Program Files (x86)\Steam\steamapps\common\HardReset\data\shaders\` — **new folder, created by
   us**, holding `common.hlsl` (unmodified copy from the archive) and `ppToneMapping.hlsl` (archive copy
   with one added line before `return color;`: `color.xyz *= float3( 1.0, 0.25, 0.25 );`, marked
   `MOD TEST`). If the loose-file route works, **the whole game will look red**.
2. `Documents\Hard Reset Extended\profiles\tefmeister\config.cfg` — **one line appended:
   `r_shader_cache "0"`**. The game's own saves also left `r_stereo_eye_separation "5"` in there.

**To run the test:** start the game, load, look. Red = loose shaders are compiled (a no-injection
route to a first per-eye camera). Noticeably slower start-up without red = the cache is off but the
archive copy won. No change at all = the setting may load too late; next try is renaming
`cache\cache.bin`. **To undo:** delete the `data\shaders\` folder and the `r_shader_cache "0"` line.
Neither file is game content we ship; nothing from them is committed.
