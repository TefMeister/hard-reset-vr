# /gr → engine-research: Hard Reset is publicly listed as a 3D Vision Direct Mode game

From: `/gr` estate sweep, 2026-09-29. Full write-up: `external-research/topics/2026-09-29-hard-reset-is-a-3d-vision-direct-mode-game.md`.

**Bears on:** dossier §11 ("the built-in stereo renderer is very probably NVIDIA 3D Vision, not the game's own doubling") and the board's NVAPI `[PD]` row.

- The open-source stereo wrapper **wiz3D** lists Hard Reset (DX9, x86) among 3D Vision **Direct Mode** games, meaning games that render both eyes themselves and choose the eye with *SetActiveEye* `[reported]`.
- Its maintainer reports Hard Reset working after a September 2026 fix. The game calls *Stereo_Deactivate* at start-up as a handshake ("I do my own stereo"). Taken literally, that call makes the game fall back to mono and never reach Activate or SetActiveEye. Ignoring a Deactivate that comes before the first Activate lets it render each eye every frame `[reported]`.
- ⚠️ The §11 evidence (no per-eye code in any world shader) is **also what Direct Mode looks like**, because the per-eye camera is set on the CPU side, so it does not tell the two readings apart `[hypothesis]`.
- The 2026-09-14 live result (a blown-out picture, a buffer in the corner, separation made no difference) fits "the stereo path started, but the driver never said stereo was active" `[hypothesis]`.

**Suggested separating step (no game needed):** in the exe, find the call order of the stereo NVAPI IDs (Deactivate → IsActivated → Activate → SetActiveEye per frame). If that order is there, a logging `nvapi.dll` of our own that answers "active" is the one `[FLAT]` test that decides it. Success is SetActiveEye being called twice per frame.
