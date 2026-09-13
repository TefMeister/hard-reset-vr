# Engine Dossier — Hard Reset (Road Hog Engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `dev-archive/` and `modding-notes/` folders; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0, first static look (2026-09-13); the game has not been launched yet. · **VR-readiness verdict:** TBD. Nothing seen so far rules it out.

## 1. Identity
- Game / build / version: Hard Reset, Steam build, exe `hardreset.exe` (linked 2012-04-26, the Extended Edition era rather than the later Redux).
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC). Official release, not a fan port.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: Flying Wild Hog's own Road Hog Engine `[reported]`. Havok, FMOD, Bink and NVAPI are in use `[inferred-static 2026-09-13]`.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.):
- Distinctive file formats / build tags / symbol naming: Data under `data\`, not yet looked at.

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): **32-bit** (PE32), `hardreset.exe` 7.3 MB, linked 2012-04-26. Plain sections (`.text`, `BINK`, `.rdata`, `.data`, `.rsrc`), with no protection-shaped section `[inferred-static 2026-09-13]`.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: Direct3D 9: `d3d9.dll` in the exe's strings, with `D3DX9_43.dll` and `D3DCompiler_43.dll` shipped beside it `[inferred-static 2026-09-13]`.
- Developer console / cvar system present? how opened?: not yet investigated.

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: Steam API only; no wrapper or protection section found `[inferred-static 2026-09-13]`. Not tested live.
- Attach workflow that works: not yet tested.
- Injection vector that works (proxy DLL name / injector / framework): not yet tested.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)
- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention:
- Where projection `P` / FOV comes from:
- The per-eye override maths (`K_eye = …`):

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap):
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?:
- The chosen override patch point and why:

## 8. Pass inventory (by render target)
- Main scene (res/formats):
- Shadow passes (depth-only sizes):
- Post / AA chain (SMAA/TAA/motion vectors; downscale sizes):
- UI / HUD (how it's kept separate):

## 9. cvar / console cheat sheet
| command / cvar | effect | use |
|---|---|---|
| | | |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used):
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- none yet.

## 12. Open risks toward the North Star
- Nothing blocking seen yet. A small, unprotected 32-bit Direct3D 9 exe is the friendliest starting point of this batch.
