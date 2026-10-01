# 2026-10-01 (`/pd`, dev PC): Hard Reset draws two eyes from a console setting, and tells NVIDIA which eye

**The game was not launched, and nothing here has been run.** Read from `hardreset.exe` on disk (fixed base
`0x400000`, no protection on the code).

## What the code does `[inferred-static 2026-10-01]`

- **NVIDIA's library is loaded by name at run time**, not imported: `0x6bd0c0` does `LoadLibrary("nvapi.dll")` and
  `GetProcAddress("nvapi_QueryInterface")`, then looks every function up by its ID. ⚠️ This corrects the dossier,
  which said the import table carried it. `LoadLibrary` searches the game's own folder first, so a `nvapi.dll` of
  ours placed beside the exe is the one the game gets `[hypothesis]` (standard Windows search order; not tried here).
- **The whole NVAPI library is linked in**, so every wrapper exists; only these are called: create/destroy a
  stereo handle, Activate/Deactivate, IsActivated, IsEnabled/Enable, GetSeparation, GetEyeSeparation,
  **SetDriverMode** and **SetActiveEye**. SetSeparation, SetConvergence, SetSurfaceCreationMode and
  ReverseStereoBlitControl are never called.
- **Start-up (`0x973694`):** Initialize, then **`SetDriverMode(2)` = direct mode** (the game draws each eye itself),
  then IsEnabled → Enable.
- **Every frame (`0x973700`):** the eye count at `[0xdccfe8]` = **1 + (`[eax+0xdcc134]` ≠ 0)**, a console-variable
  byte — very probably `r_stereo_enable` `[inferred-static]` — and then `0x9731a0` activates or deactivates driver
  stereo, which it allows only if the driver reports stereo enabled **and** `[0xbc1bb8] == 0x78` (120, most likely a
  120 Hz refresh requirement `[hypothesis]`).
- **So the two-eye loop runs from the console setting alone**, driver or not: `0x976336` loops over the eye count
  (`0x8a6b60` per eye), and before each eye's draw `0x976d4f` and `0x96b036` call **`SetActiveEye(handle, eye
  index 0 → 2 (right), 1 → 1 (left))`** when the count is above 1. Per eye, `0x96f14b` picks a ± constant
  (`[0xa9574c]` / `[0xa71064]`) for the eye shift.
- **This explains the 2026-09-14 live result:** `r_stereo_enable 1` made a blown-out picture with a small foreign
  buffer in a corner. The game was drawing both eyes into one screen with no driver to separate them; nothing was
  broken, it was the second eye landing on the first.

## The VR route this opens

A stand-in `nvapi.dll` beside the exe that answers `nvapi_QueryInterface` for the IDs above: report stereo
supported and enabled, accept direct mode, hand out a dummy handle, and in **`SetActiveEye` learn which eye is about
to be drawn**. That is the moment to switch the render target to that eye's texture (and to the headset's eye
projection), and the frame then arrives already split by eye. Everything else in the library can return "not
supported".

## Not established

- That `[eax+0xdcc134]` is `r_stereo_enable` (name not tied to the address yet; the live toggle behaves exactly as
  this predicts).
- What the per-eye constants are, and whether the eye shift reaches the world shaders (the shipped HLSL only shows a
  per-eye term in the HUD shaders, so the separation may be applied CPU-side to the camera).
- Whether the game creates its own per-eye targets or relies on the driver to split the back buffer (the latter
  fits the live picture).
