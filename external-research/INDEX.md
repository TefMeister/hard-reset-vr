# Research index

**Last `/gr` pass: 2026-10-04 (estate sweep) — CHECK-IN.** Inbox empty. Read our fake `nvapi.dll` against wiz3D's Hard Reset fix: ours always answers "stereo not activated", the answer wiz3D found makes the game drop to mono; pointer sent to the dossier inbox.

_Previous: **Last `/gr` pass: 2026-09-29 (estate sweep) — CHECK-IN.** The open-source wiz3D stereo wrapper lists Hard Reset as a 3D Vision Direct Mode game that draws both eyes itself, and got it working in September 2026; topic filed and a pointer sent to the dossier._

_Previous: **Last `/gr` pass: 2026-09-23 (estate sweep) — CHECK-IN.** Checked phunkaeg's *VR Modding Playbook*: no entry for this engine or game. Nothing new.

_Previous: **Last `/gr` pass: 2026-09-17 (estate sweep) — CHECK-IN.** First pass: folder bootstrapped; one short topic confirming the loose-file priority and console key in public, and noting that nothing public covers `r_stereo_enable`._

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **looked at** — the modding side has read it; no verdict yet.
- ✅ **used / confirmed** — acted on, and it held.
- ❌ **dead end** — tried, and it did not work (kept so it is not re-proposed).

| Date | Topic | Status | Why it matters |
| --- | --- | --- | --- |
| 2026-09-29 | [Hard Reset is listed as a 3D Vision "Direct Mode" game: it may draw each eye itself](topics/2026-09-29-hard-reset-is-a-3d-vision-direct-mode-game.md) | 🆕 | Answers the NVAPI `[PD]` row's question in public: the game may render both eyes itself, and an `nvapi.dll` of ours could switch that on |
| 2026-09-17 | [Public notes confirm loose files override archives and give the console key; `r_stereo_enable` is undocumented](topics/2026-09-17-loose-files-and-console-public-notes.md) | 🆕 | Backs the loose-shader test already set up, and marks the stereo cvar as ours to find |
