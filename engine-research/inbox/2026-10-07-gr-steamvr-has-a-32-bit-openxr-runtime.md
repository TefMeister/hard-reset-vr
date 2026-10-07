# SteamVR 2.17+ has a 32-bit OpenXR runtime

From `/gr`, 2026-10-07. Topic: `external-research/topics/2026-10-07-steamvr-2-17-ships-a-32-bit-openxr-runtime.md`.

Answers the board row *"[VR CLAUDE] (home PC) … needs a 32-bit OpenXR runtime there (check whether
SteamVR/Virtual Desktop ship one)"*: **SteamVR does, since 2.17 (stable 2026-09-10)** `[reported]`.

Suggested change: in the home-PC reminder (`owed/HOME/2026-10-07-hard-reset-in-the-real-headset-32-bit-openxr.md`,
step 2) and dossier §(xr setup), set `runtime_json=` to `…\SteamVR\steamxr_win32.json` on SteamVR 2.17+,
with Virtual Desktop's VDXR as the fallback. Not yet tried on our machines.
