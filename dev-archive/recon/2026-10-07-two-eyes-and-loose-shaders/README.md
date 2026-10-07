# 2026-10-07 — the game draws two eyes, and it compiles our loose shaders (dev PC, /lm, unattended)

Launch `steam://run/98400` (1280x720 window), Escape/Enter through films, mouse click on "Resume game" (the menu
answers absolute mouse clicks), "press any key" after the comic. Console: Ctrl+~ then typed text (`hrcon.py`;
⚠️ never name a script `con.py` on Windows: CON is a device name and python opens a prompt instead).

1. **Loose shaders are compiled** `[verified-live 2026-10-07, n=1]`: with `data\shaders\ppToneMapping.hlsl`
   (one added line, colour × (1, 0.25, 0.25)) and `r_shader_cache "0"`, the menu background and the whole game world
   came out red (gameplay R/G/B means 32.5/13.9/14.2), the HUD and comic screens untouched (not tone-mapped). So
   edited .hlsl beside the archives replace the shipped ones, with no injection. Test files taken out afterwards
   (kept in the local archive); `r_shader_cache "0"` left in the profile config on purpose.
2. **`r_stereo_enable 1` makes the game draw both eyes** `[verified-live 2026-10-07, n=1]` with our nvapi.dll in
   PASS-THROUGH (real driver): SetActiveEye alternates LEFT/RIGHT, ~119/s each (590-600 per 5 s), mono 0, steady for
   over a minute. The real driver answers `Stereo_IsActivated` with status -140 but activated=1, ~60 calls/s.
   SetDriverMode(DIRECT) still returns -219.
3. **The window stops updating** once stereo is on (the last frame stays, the game keeps running and drawing eyes);
   `r_stereo_enable 0` typed blind did not visibly land, so the game was ended with taskkill (it was not saved to
   the config). The eye pictures go somewhere we cannot see yet: the next step is a d3d9 proxy that sends each eye's
   draws to its own half of a surface (the wiz3D DX9 shape, idea only).
