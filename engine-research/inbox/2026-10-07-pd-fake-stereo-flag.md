# The nvapi stand-in's fake mode now remembers Activate, and logs the game's stereo gate

From: the `/lm` session's static reader helper, 2026-10-07. Answers
`inbox/2026-10-04-gr-fake-stereo-answers-not-activated.md`. Nothing run against the game.

## What changed in `staging/hard-reset-vr/proxy-nvapi/`

- **Fake mode keeps an "activated" flag** `[compile-verified 2026-10-07]`: `Stereo_Activate` sets it, a `Deactivate`
  clears it only if an Activate has already happened; a Deactivate before the first Activate is ignored and logged
  as such. `Stereo_IsActivated` reports the flag. Idea credited to wiz3D's Hard Reset fix; no code copied.
- **New marker `nvapi_fake_always_activated.txt`** (only with `nvapi_fake_stereo.txt`): `IsActivated` always 1.
- **Every stereo call is logged with its answer**; `SetActiveEye` is logged one by one for the first 12 calls, then
  as per-5-second counts that now include non-zero answers (it runs twice a frame).
- **Once-a-second read-only watch**, only when the exe is `hardreset.exe` at base `0x400000`: logs `[0xbc1bb8]`
  (DWORD), `[0xbc1daa]`, `[0xbc1bec]`, `[0xbc1dab]` (bytes), the handle `[0xbc1dac]` and the eye count `[0xdccfe8]`.
  Reads go through `ReadProcessMemory` on our own process, so a bad address fails instead of crashing; the dll pins
  itself so the thread's code cannot be unloaded. The watch path is `[compile-verified 2026-10-07]` only: the
  self-test is not `hardreset.exe`, so it logged "memory watch off" as designed.
- Self-test: `pass` 6/6, `fake` 10/10, `always` 10/10 `[verified-numerically 2026-10-07, n=1 each]` (new check:
  early Deactivate → 0, Activate → 1, later Deactivate → 0, Activate → 1; always mode 1/1/1/1).
- Exports unchanged: `nvapi_Direct_GetMethod @1`, `nvapi_QueryInterface @2` `[compile-verified 2026-10-07]`.
- Build: `build/nvapi.dll`, SHA-256 `cfd70f900faf9173...` (full `cfd70f900faf91737c4a10d2cb2d85e491aa56373c7ec35f1ab8aee3e0bbc601`),
  reproducible across two rebuilds. Not deployed to the game folder (the reader never touches it).

## Static read of the decision at `0x9731a0` (correction to the dossier wording)

Read 2026-10-07 from the shipped exe `[inferred-static 2026-10-07]`:

1. `want` = the argument. If `want == [0xbc1dab]` (the cached state) → return. Nothing happens unless it changes.
2. Calls **IsActivated** (`0x6cc210`, ID `0x1FB0BC30`) on handle `[0xbc1dac]`, writing the answer over the argument
   slot. A non-zero NVAPI return → return without changing anything.
3. `want` is forced to 0 if `[0xbc1daa] == 0`, or `[0xbc1bec] == 0`, or **`[0xbc1bb8] != 120`**.
   ⚠️ The 120 test is a **DWORD** compare (`cmpl $0x78`), not a byte one as "the byte at 0xbc1bb8" suggests.
4. If `want` differs from the IsActivated answer: `want` → **Activate** (`0x6cc090`, `0xF6A1AD68`), else
   **Deactivate** (`0x6cc150`, `0x2D68DE96`). A failing call → return.
5. Stores `want` to `[0xbc1dab]` and calls `0x951770` on the object at `0xdd1b58` with it.

What this means for the launch `[hypothesis]`:
- If `[0xbc1bb8]` is not 120 on a 60 Hz desktop, the game never calls Activate at all, so the flag mode answers 0 and
  nothing changes from the old fake mode; the watch line shows `FAIL` and is the deciding reading.
- If it is 120, flag mode lets Activate happen and later IsActivated calls agree with it.
- An IsActivated answer of "no" does not stop the eye loop in this function; whether `0x951770` or another caller
  (wiz3D's start-up Deactivate path) gates the second eye is still open.
- If the gate fails, the next separating step is to find who writes `[0xbc1bb8]` (probably the display refresh
  rate) rather than to answer differently from the dll.
