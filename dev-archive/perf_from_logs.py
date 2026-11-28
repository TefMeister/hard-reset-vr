"""perf_from_logs.py - what each kept Hard Reset run spent its frames on, from the add-on's own counters (2026-11-28).

    python perf_from_logs.py <d3d9_proxy_log.txt>...

Only seconds in play count (the last weapon line says a morph 0..9 and the headset hands frames over). Prints the
medians: frames a second, eye size, game draws per frame, gun constant uploads per frame (our hook), the copy of the
eyes (ms per frame), and how many of the frame's milliseconds those leave unexplained."""
import re, statistics, sys

for path in sys.argv[1:]:
    eye = "?"; in_play = False; rows = []
    cur = {}
    for l in open(path, "rb").read().decode("latin1").splitlines():
        m = re.search(r"xr: two (\d+x\d+) eye swapchains", l)
        if m: eye = m.group(1)
        m = re.search(r"weapon: morph (-?\d+)", l)
        if m: in_play = int(m.group(1)) >= 0
        m = re.search(r"\] per s: present (\d+) .*draws to back buffer (\d+) / elsewhere (\d+)", l)
        if m:
            cur = dict(fps=int(m.group(1)), draws=int(m.group(3)))
        m = re.search(r"memcpy ([\d.]+)/", l)
        if m and cur: cur["copy"] = float(m.group(1))
        m = re.search(r"gun per s \(ON\): object matrices set (\d+).*bones (\d+)", l)
        if m and cur: cur["consts"] = int(m.group(1)); cur["bones"] = int(m.group(2))
        m = re.search(r"graft per s: anchor draws seen (\d+).*game parts hidden (\d+)", l)
        if m and cur: cur["hidden"] = int(m.group(2))
        if l.find("ghost hand per s") >= 0 and cur:
            if in_play and cur.get("fps", 0) > 5 and "copy" in cur:
                rows.append(cur)
            cur = {}
    if not rows:
        print("%s: no seconds in play" % path[-45:]); continue
    med = lambda k: statistics.median(r.get(k, 0) for r in rows)
    fps = med("fps")
    per = lambda k: med(k) / fps if fps else 0
    print("%s | eye %s | %d s in play | %.0f fps (%.1f ms) | draws/frame %.0f | gun consts/frame %.0f | hidden/frame %.0f | "
          "eye copy %.2f ms" % (path[-45:], eye, len(rows), fps, 1000 / fps, per("draws"), per("consts"), per("hidden"),
                                med("copy")))
