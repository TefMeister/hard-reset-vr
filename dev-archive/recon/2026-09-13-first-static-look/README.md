# First static look (2026-09-13)

Read from the installed Steam copy on the home PC, without launching the game. Every claim
below is `[inferred-static 2026-09-13]` unless tagged otherwise: it comes from reading file headers
and strings, not from running anything.

- **Install:** `HardReset`, 4.5 GB.
- **Identity:** Hard Reset, Steam build, exe `hardreset.exe` (linked 2012-04-26, the Extended Edition era rather than the later Redux).
- **Engine:** Flying Wild Hog's own Road Hog Engine `[reported]`. Havok, FMOD, Bink and NVAPI are in use `[inferred-static 2026-09-13]`.
- **Binary:** **32-bit** (PE32), `hardreset.exe` 7.3 MB, linked 2012-04-26. Plain sections (`.text`, `BINK`, `.rdata`, `.data`, `.rsrc`), with no protection-shaped section `[inferred-static 2026-09-13]`.
- **Renderer:** Direct3D 9: `d3d9.dll` in the exe's strings, with `D3DX9_43.dll` and `D3DCompiler_43.dll` shipped beside it `[inferred-static 2026-09-13]`.
- **Protection:** Steam API only; no wrapper or protection section found `[inferred-static 2026-09-13]`. Not tested live.
- **Other files:** Data under `data\`, not yet looked at.

## Method

PE headers read with a short script: machine type, link timestamp, section names and sizes.
Then a case-insensitive search of each binary for renderer DLL names (`d3d9`, `d3d11`, `d3d12`,
`dxgi`, `vulkan-1`, `opengl32`), protection markers (`denuvo`, `securom`, `.bind`) and middleware
names. A string match shows a name is present in the file, not that the code path is used.

## Risks noted

- Nothing blocking seen yet. A small, unprotected 32-bit Direct3D 9 exe is the friendliest starting point of this batch.
