Hard Reset VR 0.1.0


CAUTION: this mod is unfinished and still being worked on. VR can cause severe motion sickness and discomfort, and
an unfinished VR mod even more so. Stop playing at once if you feel unwell, and take breaks.


Description


Plays Hard Reset (Extended Edition) in a VR headset: the game is drawn in 3D, a picture for each eye, and the view
follows your head, including leaning and stepping. The 3D switches on by itself when the game starts.
You play with mouse and keyboard as normal.

What this mod is: a few small files of our own that sit next to the game. What it is NOT: it contains no game files,
it does not change the game's own files, and it is not made or supported by Flying Wild Hog. You need your own copy
of the game.


Installation instructions


STEP 1 - The game

1.1  Install Hard Reset Extended from Steam (only tested with the Steam version).

1.2  Find the game folder: in Steam, right-click the game > Manage > Browse local files. This is the folder that
contains hardreset.exe. Every "game folder" below means this folder.

1.3  Start the game once, make your player profile when it asks, reach the main menu, and quit. (This lets Steam
and the game finish their setup. Steam may ask Windows for permission the first time; click Yes.)


STEP 2 - Your headset

2.1  Connect your headset to the PC the way you normally play PC VR. Tested with a Meta Quest 3 through Virtual
Desktop.

2.2  The game is 32-bit, so your headset software must offer a 32-bit OpenXR runtime. Virtual Desktop does this by
itself. SteamVR 2.17 or newer has one too.


STEP 3 - This mod

3.1  Open the folder "HardReset" inside this package.

3.2  Copy EVERYTHING inside it into the game folder. (The full list of what is added is in FILES.txt.)

3.3  Only if the game does not show in your headset: open d3d9_vr.ini in the game folder with Notepad and point
runtime_json at your runtime's 32-bit file. The two common ones are already written there; remove the ; in front of
the one you use.


STEP 4 - Play

4.1  Start the game from Steam with the headset connected.

4.2  The game and its menus appear in the headset in 3D after a second or so. Play with mouse and keyboard.

4.3  The picture on the monitor shows both eyes side by side. Menus are drawn twice there too, so if a click does
not land, press Escape to go back a step.


UNINSTALL

Delete the files listed in FILES.txt from the game folder


Main features


the whole game in 3D in the headset, a picture for each eye
the view follows your head, including leaning and stepping
the 3D switches on by itself


Known problems


the menus and HUD work, but their frames can look rough
the frame rate is held back by one copy step that will be improved


Requirements


Hard Reset Extended (Steam)
a PC VR headset with a 32-bit OpenXR runtime (Virtual Desktop, or SteamVR 2.17 or newer)


Shout outs


Flying Wild Hog for Hard Reset
Claude Code for all the coding
the wiz3D project (https://github.com/effcol/wiz3D) for showing the game draws both eyes itself
The Khronos Group for the OpenXR loader (openxr_loader.dll, Apache License 2.0, included as LICENSE-OpenXR-loader-Apache-2.0.txt)

If you helped or inspired this and are not listed, email td3kxlvr@proton.me and it will be fixed as soon as
possible. We honour correction and removal requests from rights holders.
