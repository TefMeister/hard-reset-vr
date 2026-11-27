# 2026-11-27 evening: Tefa's Meshy gloves as bendable VR hands, and the Skin Checker add-on

Done together in live Blender (MCP for Blender), Tefa watching and placing the joint spots by hand.

## What was tried, in order

1. **Rigid pieces** (each finger cut into 3 at Tefa's 15 joint spots, a bone per piece, lids on the cuts, rounded
   knuckle fillers): open ends and filler balls showed at every bend. **Tefa rejected it** ("it needs a different
   approach") `[verified by eye 2026-11-27]`.
2. **Skinning** (one uncut glove, the same 16 bones, the surface stretches across each joint): smooth from a
   distance, but Tefa's close-ups found torn flaps, shards through the skin and a crumpled thumb web.

## Why it tore: the import splits the glove into patches

A Meshy `.glb` imports into Blender as **546 separate patches** (the surface is split along every texture seam).
Points that look like one point belong to different patches, get different pulls, and come apart at a bend.
**Merge by Distance at 0.02 mm before slimming** makes it one connected surface (the texture is kept)
`[measured 2026-11-27, n=1: 546 -> 1 patch after rebuilding from the original download]`.

## Measured with the new checker (grip pose, right glove)

| step | stretched/crushed edges (worst) | new clipping | torn edges |
| --- | --- | --- | --- |
| first skinning | 2776 (22.8x) | 3427 | 656 |
| + layers blended 8-12 mm in space | 949-1035 (5.5-6x) | 2538-3210 | 199-282 |
| + stitched into one surface | 687 (32x) | 772 | 167 |
| + neighbouring fingers blend 40 mm past the knuckle (Meshy joins touching fingers along their sides) | **620 (2.9x)** | **535** | **0** |

Trigger-finger pose (index straight, others gripping): 513 / 310 / 0; the straight index is not dragged by its
neighbours (checked by picture). Tight fist: 1516 / 2460 / 0 (much self-contact, as in a real fist). What clipping
is left sits on the inside of the bends and where fingertips meet the palm; in the game a gun handle fills that.
Preserve Volume (dual quaternion) made every number slightly worse: left off.

## The Skin Checker add-on (ours)

`dev-archive/blender/skin_checker/` (installed in Blender 5.3's add-ons, switched on). Side panel -> Skin Checker:
Stitch patches, Make weights (nearest finger, stretch across each joint, then averaged in space so stacked layers move
as one; fingers blend with neighbours only near the knuckle), test poses (grip, trigger finger out, fist, open), Check
bend (stretch, new self-clipping against rest, torn edges, marked in red), Next spot, Clear marks. Tefa asked for it
to be our own add-on ("please save that tool as our own add-on in blender").

## Files (work folder `D:\claude video game stuff\blender\hard-reset-vr\meshy hands`)

`originals/` (Tefa's downloads), `meshy_hand_right_cut.blend` (rigid pieces, rejected, kept),
`meshy_hand_right_rigged.blend` (pieces on bones, kept), `meshy_hand_right_skinned.blend` (the current one).

## Next

Tefa's eye on the skinned glove; then the left glove the same way (stitch first); then the add-on (hr_hands.c) learns
to bend a skinned mesh (it draws rigid parts today), and the grip point is set.

## Later the same evening: fingers going thin at the bends (Tefa's eye)

Tefa: "these are parts that look like they get thinner to avoid clipping, but they have to be thicker" (the inside
of bent bare fingers). The checker had no measure for it, and had wrongly counted Preserve Volume as worse (more
contact) when it is what keeps a finger full. New measure: per joint, the width of the ring of skin round it, bent
against straight (open pose = 1.00 everywhere). Grip, before: index middle joint 0.73, thumb tip joint 0.78-0.81,
middle finger middle joint 0.82-0.87.

Fix: **Preserve Volume on, and every finger hinge moved 4 mm towards the inside of its bend** (the thumb tip joint
6 mm more), as a real knuckle turns nearer the palm side; end-joint stretch 10 mm. Grip after: every joint 0.90 or
more, clipping 637 -> 260, torn 0; trigger pose clipping 93; fist joints 0.88 or more. Checked by picture at Tefa's
three spots: full, rounded bends. 5 mm was thicker still but brought the first tear and 7x stretch on the knuckle
backs. The add-on gained "Hinges towards palm" and the per-joint thickness line in Check bend.
