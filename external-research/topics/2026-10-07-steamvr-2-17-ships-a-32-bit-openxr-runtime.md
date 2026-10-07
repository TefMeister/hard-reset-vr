# SteamVR 2.17 ships a 32-bit OpenXR runtime

**Status:** 🆕 new · **Priority:** high — it answers the home-PC `[VR CLAUDE]` row's first question.

## What is public

- **SteamVR 2.17 left beta on 2026-09-10**, and its notes say: *"Added support for 32-bit OpenXR
  applications."* `[reported 2026-10-07]`
- How it is switched on: after installing, SteamVR **prompts to become the default OpenXR runtime**, and
  accepting registers the runtime in **both** places the OpenXR loader looks: the normal key and the
  32-bit one under `HKLM\SOFTWARE\WOW6432Node\Khronos\OpenXR\1\ActiveRuntime` `[reported]`.
- Our own dev PC already saw the file side of this: SteamVR there ships `steamxr_win32.json`, but the
  32-bit registry key was **empty** (Alan Wake dossier, `[measured 2026-10-06]`). That matches the
  public account: the file is shipped, the key is only filled when SteamVR is (re)set as the default.

## Why it matters here

Hard Reset is a 32-bit Direct3D 9 game, and our `d3d9.dll` bridge talks OpenXR through a 32-bit loader.
The home-PC reminder says *"find a 32-bit OpenXR runtime json (SteamVR or Virtual Desktop)"*. On SteamVR
2.17 or later the answer is now concrete:

1. Point `d3d9_vr.ini` `[xr] runtime_json=` straight at
   `…\Steam\steamapps\common\SteamVR\steamxr_win32.json` (needs no registry change at all), **or**
2. In SteamVR's settings, set SteamVR as the OpenXR runtime again, which should fill the 32-bit key.

Option 1 is the smaller change and leaves the machine's settings alone. Virtual Desktop's VDXR remains the
fallback: XIII reached the headset through it from a 32-bit game on the home PC `[reported]`.

⚠️ **Not yet checked on our machines:** that the home PC runs 2.17+, and that a 32-bit app actually gets a
working session from `steamxr_win32.json`. Two public news write-ups and Valve's one-line note are the
whole evidence so far.

## Sources

- vr.org, "SteamVR 2.17 stable, 32-bit OpenXR runtime" (2026-09-12) —
  <https://vr.org/articles/steamvr-2-17-stable-32-bit-openxr-runtime-2026>
- GamingOnLinux, "SteamVR 2.17 arrives ready to go for the Steam Frame" (2026-09) —
  <https://www.gamingonlinux.com/2026/09/steamvr-2-17-arrives-ready-to-go-for-the-steam-frame/>
