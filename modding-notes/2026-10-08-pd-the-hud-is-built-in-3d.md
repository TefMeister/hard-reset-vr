# 2026-10-08 (`/pd`, dev PC): Hard Reset's HUD is built in 3D on purpose — leave it there

**The game was not launched, and nothing here has been run.** Read from the game's own archives (opened with the
key from `dev-archive/recon/2026-09-14-archive-and-shader-pass/unlock_archives.py`, kept outside every repo; nothing
extracted is committed).

## What the game does `[inferred-static 2026-10-08]`

- **The HUD is an item with a 3D model:** `data/items/hud/hud.rhs` (+ its own animation `hud.hkx` and textures),
  spawned by the script template `gameplay/base_templates/item/hud.nut`.
- That script creates **two animated screens and attaches them to the player's model**:
  `animatix_hud_3d_stats` at the attachment slot `arm02_attachment` (radar, health, shield, two ammo counters:
  `animatix/hud/hud_stats.aix`) and `animatix_hud_3d_bars` at `main_attachment` (health / shield / energy / sprint /
  experience bars: `hud_bars.aix`). Both are drawn by the `animatix` shader with a world-space (perspective) matrix,
  which is exactly the `not screen-space ~1300/s` the panel test counted, together with the in-world holo screens.
- **A flat 2D HUD also exists and is never used:** `animatix_hud_2d` (`hud/hud2d.aix`: radar, level, experience,
  health, shield, ammo) is referenced by no other script in any archive.
- The flat, screen-space `animatix` / `font` draws are the overlays: crosshairs (`hud/crosshair*.aix`), damage
  indicators and blood (`hud/damage_indicator*.aix`, `hud/blood*.aix`), and the menus, loading and briefing screens
  (`hud/menu_*.aix`, `loading*.aix`, `briefing.aix`). In gameplay that is about one draw a frame, which matches the
  panel test's `placed 60-70/s` `[verified-live 2026-10-08, n=1]`.

## The decision

**Leave the health dial and the bars where the game puts them.** They are 3D screens on the arm and the gun, so they
already have correct depth in both eyes and follow the player's hands, which is what a VR HUD should do. Nothing to
build.

**Use the panel only for what is flat:** crosshair, damage indicators, menus, loading and briefing screens. The panel
code is already built (`d3d9_hud.txt`, 2026-10-07); what is left is to look at it with those on screen.

## Not established

- Which of the two screens Tefa called the "dial" (the stats screen on `arm02_attachment` is the likely one).
- Whether a head-locked crosshair 2 m ahead is comfortable, or whether it should sit at the aim distance instead.
- The `hud_solid` and `r_draw_hud_refraction` switches (in the exe) probably change how the 3D screens look
  (solid versus see-through); untried.
