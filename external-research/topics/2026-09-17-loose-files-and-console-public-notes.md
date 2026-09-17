# Public notes confirm loose files override archives and give the console key; `r_stereo_enable` is undocumented

**Status:** 🆕 new · **Priority:** low — it confirms rather than adds.

## What is public

- PCGamingWiki: the console opens with **Ctrl + ~**, and the game **reads both archives and loose files,
  preferring loose files** `[reported]`.
- No public source was found for `r_stereo_enable`, Squirrel script execution from the console, or a 3D
  Vision fix `[reported 2026-09-17, n=1 search]` — an automated search coming up empty is not proof
  nobody has done it.

## Why it matters here

The `[FLAT]` loose-shader test rests on loose-file priority; the public record agrees. The stereo cvar and
script execution remain this project's own findings to make.

## Sources

- PCGamingWiki, Hard Reset — <https://www.pcgamingwiki.com/wiki/Hard_Reset>
- Steam discussion, "Console commands, Cheat Codes" — <https://steamcommunity.com/app/407810/discussions/0/4522261213599248315/>
