# Our own guns: five bullet guns, five energy guns, and melee

Order: 24000
From: the ideas repo, `games/hard-reset.md` (<https://github.com/TefMeister/mod-ideas/blob/main/games/hard-reset.md>), copied 2026-11-28

`[raw]` · `[looks doable]` — *the add-on already draws our own models inside the game's gun; a whole gun per mode is unchecked*

> "what we might do, is actually make guns for this game, 5 physical guns and 5 energy ones. and i think there is melee
> as well"

Instead of one gun that morphs, ten separate guns built in Blender, one per mode, each made to look like its own weapon
(Meshy for the shape, then cleaned up together).

**What it'd take:** the "graft" in the add-on (2026-11-27) already hides game parts and draws Meshy's frame inside the
game's own gun draw, lit like the gun, and the ripper has every mode's model out of the game. A whole gun per mode is
the same trick taken further: hide every part of that mode and draw our gun in its place. What is unknown: the game
animates the morph between modes and the moving parts (barrel, drum) when firing; a gun of our own either gets those
movements from the game's bones (the parts we hide carry them) or does without, so the switch between modes would need
its own look (a dissolve or a quick swap). **Melee:** unchecked whether Hard Reset has a melee attack at all; our notes
do not mention one. First step is looking at the game's controls and scripts.
