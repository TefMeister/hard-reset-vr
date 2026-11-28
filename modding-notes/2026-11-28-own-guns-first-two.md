# 2026-11-28 evening (Build PC, Fable, no game running): our own guns, the first two built and installed

Tefa: "let's see if this idea is actually doable, different guns instead of one morphing gun, try the first assault
rifle and shotgun please, and the hands, and if this works, we'll do the rest soon". Files: Meshy's textured GLB and
Meshy's part-split GLB of each gun, in `D:\Hard Reset GLB` (work folder `work` inside it; our own models, Meshy-made).

## Meshy's split copy has no paint: how the parts got it back `[measured 2026-11-28, n=2 guns]`

The part-split GLB has no UVs and no textures, is about 15.86 times smaller than the textured one and stands on z 0,
but its parts have the same shape. `dev-archive/blender/own_guns_split.py`: split parts laid over the textured model
by bounding box, the textured model slimmed to 20,000 faces with its UVs, each face given the nearest part, then
separated. Gap to the part: rifle median 2 mm, shotgun 5 mm (on a 1.9-unit model). Result: rifle 6 parts, shotgun 5,
each with the original colour / roughness-metal / normal maps (2048). Looked at in Blender: clean.

## Into the game: the whole gun through the graft, every game gun part hidden `[compile-verified: files built, NOT yet seen in game]`

`dev-archive/blender/build_own_guns.py`: each gun is put in its mode's rip frame with its muzzle tip on the game gun's
muzzle tip (so the muzzle flash should still start at the muzzle) and its barrel on the game gun's front centre, then
`graft_build.py --keep-uv --tex --hide <every gun group of that rip>` (all groups but the HUD dial and the crosshair).
No change to `hr_graft.c` was needed: a hidden anchor still triggers our draw (`h_dip` calls `after_draw` after a
fully hidden draw).

- rifle -> cln1: 0.80 m long, 20,000 triangles, 50 game parts hidden; shotgun -> cln2: 0.85 m, 20,000 triangles, 44 hidden.
- Game gun measured in the rips: 0.69 m from the back end to the muzzle, muzzle tip 0.853 m (cln1) / 0.847 m (cln2)
  ahead of the eye along the gun's own axis.
- Hand spots, estimated from the model's outline (not judged by eye yet):
  `[pose.cln1] gun_grip = 0.209 -0.312 -0.355`, `foregrip_ahead_m=0.328`, `foregrip_up_m=0.076`;
  `[pose.cln2] gun_grip = 0.222 -0.365 -0.325`, `foregrip_ahead_m=0.411`, `foregrip_up_m=0.049`.
- Installed in the game folder (game closed): `gun_graft_cln1.bin`, `gun_graft_cln2.bin`, the two `[pose]` sections
  of `d3d9_vr.ini`. What they replaced (yesterday's Meshy frame for cln1/cln2 and the ini) is kept in the game folder,
  `_backup-2026-11-28-before-own-guns`. cln3..cln5 and nrg1..nrg5 still hold yesterday's frames.

## NOT established

- Anything in the game: whether both guns show, sit right in the hand, how bright they are, whether the muzzle flash
  and tracers start at our muzzle, and what is lost with every game part hidden (the firing movement, the ammo dial
  parts on the gun, the mode's glow). One mistake caught before install: the hand spots were first written unscaled.
- The parts are joined into one rigid piece for this try; they are separate in the .blend for the moving parts later.
