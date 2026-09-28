# 2026-09-28 — /pd: `r_stereo_*` is a 3D Vision client; the "two views itself" question narrows to one call

Dev PC, `/pd`, no game launched, nothing run. Game at `D:\Program Files (x86)\Steam\steamapps\common\HardReset`.

## What was found `[inferred-static 2026-09-28]`

- **The four cvars are registered in one block** of static-initialiser code: `r_stereo` names at `0xA887C0`,
  `0xA887F4`, `0xA88824`, `0xA88850` (`r_stereo_separation`, `r_stereo_eye_separation`, `r_stereo_convergence`,
  `r_stereo_enable`), referenced from `0x9DB633`, `0x9DB9D2`, `0x9DBD80`, `0x9DC119`. Those sites copy the name into a
  string object and register it; the variable's storage is reached through ref-counted wrappers, so following it to its
  readers is a debugger job or a longer static trace.
- **NVIDIA's stereo interface is fully linked in, loaded at run time.** `nvapi.dll` is not imported; the exe carries
  `nvapi_QueryInterface` and the interface IDs of the whole NVAPI stereo client — `NvAPI_Initialize` once, and 16
  stereo calls four times each, among them `Stereo_CreateHandleFromIUnknown`, `Stereo_Enable`/`Activate`,
  `Stereo_SetSeparation`/`SetConvergence`, **`Stereo_SetDriverMode`** and **`Stereo_SetActiveEye`**.
- Script-side names: `SetStereoDepthCrosshair`, `SetStereoDist`; menu text: "Stereo enable", "Stereo eye separation",
  "Stereo convergence", "Force stereo, need restart".

## What it means

`r_stereo_*` drives **3D Vision**. Separation and convergence are exactly the two numbers NVAPI takes. The row's
question — can the game draw two views itself? — comes down to one thing: **does it call
`NvAPI_Stereo_SetDriverMode` with direct mode and then `SetActiveEye` per eye?** In direct mode the *game* draws each
eye; in the default automatic mode the *driver* doubles the draws. ⚠️ All 16 IDs appear four times each, which is what a
linked library table looks like, so their presence proves the calls are *available*, not *used* `[hypothesis]`.

This also offers a reading of the 2026-09-14 live result (`r_stereo_enable 1` → white/magenta picture with a quarter-size
buffer in the corner): the engine switched to a stereo path that expected the 3D Vision driver to consume a special
buffer, and without 3D Vision nothing did `[hypothesis]`.

## Next, statically

Find the code that references the `SetDriverMode` and `SetActiveEye` interface IDs (each is a 4-byte constant pushed
before `nvapi_QueryInterface`) and see whether it is reached from the `r_stereo_enable` path. If the game uses direct
mode, it already knows how to draw a left and a right eye, and our job becomes feeding it headset poses.

## NOT established

- Which NVAPI calls run, and in which mode.
- What the quarter-size buffer seen live was.
