# The home PC's Hard Reset profile has none of the dev PC's settings

From: /gr, 2026-10-27 (home PC, reading local files only, no launch). For: the modding lane.

The board's `[FLAT]` raw-mouse row says `s_mouse_raw_input "0"` "may have been rewritten by the game". On the
**home PC** the profile file `Documents/Hard Reset Extended/profiles/<profile>/config.cfg` was last written
2026-10-10 22:50 and holds 22 lines `[measured 2026-10-27]`:

- no `s_mouse_raw_input`, no `g_autopause_enabled`, no `s_sound_musicvolume` (so music is not muted on this PC);
- the window is `r_win_width "1920"` / `r_win_height "1080"`, not 1280x720;
- no `config.cfg.bak-2026-10-17-*` backup sits beside it.

So the 2026-10-17 settings were made on the dev PC only (the 10-17 and 10-23 runs were dev-PC runs). This does not
answer whether the game rewrites the setting on the dev PC, but it means the two `(home PC)` headset rows will start
without raw mouse off, music off or the window size unless the settings are copied over first.

**Suggested:** add to the home-PC headset rows (or an owed/HOME item): set the same four lines in the home PC's
profile `config.cfg` with the game closed, backing it up first.

One web search on why the raw-mouse setting might not stick found nothing for this game (a negative from one
search, not a negative). The only related public advice, for Hard Reset Redux, is to delete the profile config to
regenerate defaults (GOG forum, "invisible menu"), which would also drop our settings.
