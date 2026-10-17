# 2026-10-17 (dev PC, simulator, VR Bench poses): the game's own gun sits at the controller

Until today the gun turned with the controller (2026-10-16) but stayed where the game holds it, at a fixed spot
in front of the eye. Now it goes where the controller is.

## How

The game places every object with three shader registers, VS c16-c18 (`float4x3 mObjectToWorld : register(c16)` in
its own `common.hlsl`, one column per register, the place in each register's last number). Each frame, while the
game builds its camera, the mod works out one move: from where the game holds the gun (a spot in front of the eye,
`[gun] grip_x/y/z` in `d3d9_vr.ini`, first guess 0.20 right, 0.25 down, 0.40 ahead) to the gun hand's controller. On
the drawing side, every object the game draws within 0.9 m of its eye gets that move.

- First try: only the object matrix was moved. In the pictures only the HUD dial moved; the gun stayed.
- The gun body is skinned: its 76 bones arrive as VS c28 onward (`mSkinning`), already in world space, about half a
  metre from the eye. With the bones moved too, the gun followed the hand left, up and nearer
  `[verified-live 2026-10-17, n=1]`.
- The game builds the held gun around the eye: its object matrix sits exactly at the eye (0.00 m).

Switch: `d3d9_gun.txt` beside the exe. With it off, the log line `gun per s` still counts what it would move.
Code: `staging/hard-reset-vr/proxy-d3d9/src/hr_gun.c`, maths `hr_gun_math.c` (15 checks).

## Not right yet

- **The dial on the gun** lands in the wrong place when the gun moves: a dark slab under the gun with the hand
  moved left, low-left and large with the hand moved up (n=1).
- **The grip spot** is a guess; it should put the gun's handle in the hand.
