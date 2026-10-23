# OPEN block older than the board's newest entry

From: /gs, 2026-10-23 (dev PC). For: the modding lane.

`gate-scan.sh --check` (ref origin/main) on `claude-memory/status/hard-reset-vr.md`: OPEN dated 2026-10-17, newest log entry 2026-10-18 (second sweep running that this board needed a re-audit).
`[measured 2026-10-23]`

A stale block means a session logged work without re-auditing what is left, so `/gates` can understate. Fix:
re-audit the rows against the newest entries, then re-date the block. One line; /gs does not edit status/.
