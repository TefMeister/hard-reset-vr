# /gs 2026-10-16: open block starts with a done line

From: `/gs`, 2026-10-16. Check 7 of the sweep (`status/` OPEN gate blocks).

The OPEN block in `claude-memory/status/hard-reset-vr.md` opens with a done line (`✅ 🏆 2026-10-16 15:51 ... THE GUN FOLLOWS THE CONTROLLER`) instead of a tagged row, so `gate-scan.sh --check` reads the block as having **no rows** and `/gates` undercounts this game. Fix (modding lane): move the done line into the dated log entry below, and keep only `[PD]`/`[USER]`/`[FLAT]`/`[VR ...]` rows (or `: none`) under `OPEN (date):`. Same fault fixed on witcher-2-vr today.
