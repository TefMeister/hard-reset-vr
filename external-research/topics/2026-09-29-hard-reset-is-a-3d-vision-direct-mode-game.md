# Hard Reset is listed as a 3D Vision "Direct Mode" game: it may draw each eye itself

**Found:** 2026-09-29, `/gr` estate sweep (CHECK-IN tier).
**Answers:** the board's `[PD]` row "find the code that uses `NvAPI_Stereo_SetDriverMode` / `NvAPI_Stereo_SetActiveEye` ... direct mode would mean the game already draws each eye itself", and challenges dossier §11's reading that the stereo is driver-side doubling.

## What was found

**wiz3D** is an open-source (LGPL-2.1) stereoscopic 3D wrapper, a modernised descendant of the old iZ3D driver. One of its parts, *NvDirectMode*, stands in for NVIDIA's 3D Vision driver so that games which supported 3D Vision **Direct Mode** can show their stereo on modern displays. Its README defines that group as "games that render stereoscopic 3D themselves and display that via 3D Vision's Direct Mode", and **Hard Reset (DX9, 32-bit) is listed in that group** `[reported]`.

In wiz3D pull request #29 (closed 2026-09-18, contents merged by hand as two commits the same day), contributor **AkshayUHegde** described a handshake problem, and maintainer **effcol** confirmed it was what had kept **Hard Reset** from working "for months" `[reported]`:

- Games that render their own stereo call NVAPI's *Stereo_Deactivate* at start-up. That is not the user turning 3D off. It is the game saying "I will do the stereo myself; do not run your automatic mode on top of me".
- If the stand-in driver takes that call at face value, the game later asks "is stereo active?", hears "no", **drops to mono** and never reaches *Stereo_Activate* or *SetActiveEye*.
- With the fix (the stand-in ignores a Deactivate that arrives before the game's first Activate), Hard Reset goes on to Activate and then SetActiveEye, and **per-eye capture runs every frame** `[reported]`.

wiz3D's commit log also has "NvDirectMode/d3d9: ... Hard Reset investigation" (2026-09-18), so the work was done on the D3D9 path this project uses `[reported]`. Separately, Wikipedia's list of 3D Vision Ready games dates Hard Reset's "3D Vision Ready" status to 2011-11-10, which matches the "Full Nvidia 3dVision support" patch note already in the dossier `[reported]`.

## Why it matters for this project

- **It challenges dossier §11.** §11 reads "no world shader does anything per eye" as a sign that the driver doubles the world (Automatic Mode). In **Direct Mode** that same evidence is expected: the game draws the scene twice with a different camera each time, and picks the target eye with *SetActiveEye*. The shaders need no per-eye code. So the shader evidence does not separate the two readings. `[hypothesis]` until our own disassembly of the `SetActiveEye` call site agrees.
- **It explains the 2026-09-14 live picture** (white/magenta blow-out plus a quarter-size buffer in a corner, separation 0 vs 5 made no difference) as one possible outcome: with no 3D Vision driver present, the game's stereo path starts but never gets a "yes, stereo is active" answer, so it never draws two real eyes. `[hypothesis]`
- **It names the lever.** The exe loads `nvapi.dll` at run time (dossier §11). A small `nvapi.dll` of our own that answers the stereo questions "yes" (and does not honour the early Deactivate) and records each *SetActiveEye* call could make the game produce both eyes itself. We would then only need to pick up each eye's image and hand it to OpenXR, and would never have to edit a camera matrix. That would make this one of the cheapest stereo routes on the account. `[hypothesis]`

## Next step

1. **`[PD]`** (the existing row, now with a target): in `hardreset.exe`, find what calls the `nvapi_QueryInterface` IDs for *Stereo_Deactivate*, *Stereo_IsActivated*, *Stereo_Activate* and *SetActiveEye*, and check whether the order is Deactivate first, then a check, then Activate, then SetActiveEye each frame. If so, the game is Direct Mode.
2. **`[FLAT]`**: our own logging `nvapi.dll` that answers the stereo queries "active" and logs every call. Success is *SetActiveEye* being called twice per frame, left and right.
3. Describe the mechanism in our own words only. wiz3D's code is LGPL and **nothing is copied from it**. It is credited as the source of the finding.

## Sources

- wiz3D repository (effcol), README "Nvidia 3D Vision Direct Mode Games" table: <https://github.com/effcol/wiz3D>
- wiz3D PR #29, "NvApiProxy: add IgnoreStereoDisable so games keep their own stereo renderer" (AkshayUHegde; maintainer comment by effcol): <https://github.com/effcol/wiz3D/pull/29>
- Wikipedia, "List of Nvidia 3D Vision Ready games": <https://en.wikipedia.org/wiki/List_of_Nvidia_3D_Vision_Ready_games>
- NVIDIA NVAPI reference, stereo API group (what *SetDriverMode* direct mode means): <https://docs.nvidia.com/nvapi/group__stereoapi.html>
