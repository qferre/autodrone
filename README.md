# AUTODRONE Project
Automatic drone pathfinding and navigation

A framework to allow drones to navigate and be issued commands.

## Prerequisites

First, Blender must be installed, using `sudo snap install blender --classic`

Also pip install requirements for the Blender python interpreted, since that's the interpreter we will use

## How to use

Simply run the following command:
```
blender scenes/scene.blend --background --python scripts/main.py
```

With one of the scripts in the /scripts directory. Of course, replace scene.blend with the blend file containing the photogrammetrized mesh of the scene you wish to navigate inside of.









& python tests/octree.py
& python tests/pathfinder.py
& "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" scenes/basic.blend --background --python tests/space_representation.py
blender scenes/basic.blend --background --python tests/space_representation.py






## Code structures

This section explains the general organization and behavior of the code

The entry point is the `main.py` file