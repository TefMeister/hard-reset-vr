# A crash inside Virtual Desktop's 32-bit Oculus runtime at the end of a headset run (2026-11-28)

## What it is

Gold Digger found a crash dump from Tefa's first headset look at the Meshy gun frames (2026-11-28, about 01:42):
`0xC0000409` (a fail-fast: the program stopped itself on purpose) in `VirtualDesktop.LibOVRRT32_1.dll+0x1EABC`, Virtual
Desktop's 32-bit stand-in for the Oculus runtime, loaded into `hardreset.exe` `[measured 2026-11-28, n=1]`. Our proxy log
ran normally up to 01:41:56 (engine-research inbox drop `2026-11-28-gd-headset-run-ended-in-virtual-desktop-crash.md`).

## Why it matters here

Hard Reset is a 32-bit game and our VR path goes through Virtual Desktop when Tefa is in the headset. If the crash comes
from Virtual Desktop's 32-bit layer, it is outside our code and may come back on every headset quit or long run.

## What the public record says

- One web search (2026-11-28) found **no public report of a crash in Virtual Desktop's own `LibOVRRT32_1.dll`** `[reported 2026-11-28]`.
- Meta's developer forum has a thread on OpenXR in 32-bit processes, from a modder building a VR wrapper for an old
  DirectDraw game, crashing inside the 32-bit runtime while the same code worked in a sample; a reply there argued it was
  not 32-bit specific. No fix was posted `[reported]`. <https://communityforums.atmeta.com/discussions/dev-openxr/openxr-32bit-runtime-issues/838981>
- Older threads blame stale or mismatched runtime DLL copies; workarounds only `[reported]`.

## Next step

Open question for the modding lane: why is an Oculus-API DLL loaded at all when `d3d9_vr.ini` points at Virtual
Desktop's OpenXR runtime (something in the process asks for LibOVR)? If it happens again, compare one headset run
through SteamVR's OpenXR runtime. `[hypothesis]`
