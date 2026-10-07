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

4. **Why the window "froze"** `[verified-live 2026-10-07, n=1]` (second run, the reader's log-only d3d9 proxy
   `ca21c86a78e5` + nvapi `593876cb8aa5`): with stereo on the game still Presents 60/s with no failures and draws both
   eyes, but **every Clear of the back buffer fails** (120/s, `0x8876086c` D3DERR_INVALIDCALL), so frames pile up
   into an over-bright smear (`stereo-on-no-clear-smear.png`) — the earlier "frozen" picture was the same thing.
   `r_stereo_enable 0` recovers cleanly. Next: why the per-eye Clear is invalid (reader, static).

5. **FAKE mode from game start** `[verified-live 2026-10-07, n=1]` (d3d9 `4fdd7e04b0b4`, nvapi `593876cb8aa5`,
   `nvapi_fake_stereo.txt`): SetDriverMode → 0, IsEnabled → 1, so the start-up gate [0xbc1daa] = 1 (watched live). Then
   `r_stereo_enable 1` gave only 4 SetActiveEye calls (R, L, R, L) right after an IsActivated answered **0** from our
   flag, then stopped: eye count back to 1, no failed Clears, a normal mono picture. Reading: in this path an
   IsActivated "no" makes the game fall back to one eye `[hypothesis]`. Next run: add
   `nvapi_fake_always_activated.txt` (forces yes) from game start, keep `d3d9_sbs.txt`, then `r_stereo_enable 1`.
