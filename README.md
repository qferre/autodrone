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
& "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" scenes/basic.blend --python tests/space_representation.py
blender scenes/basic.blend --background --python tests/space_representation.py






## Code structure

This section explains the general organization and behavior of the code

The entry point is the `main.py` file


The script must be called with a Blender file like we just said. This file contains a 3D model (presumably of the scene in which you want to navigate).
This means we use Blender's Python interpreter.






A SpaceRepresentation object will then be created based on the scene. A Pathfinder object will be created for later use.
Upon specifying a destination, the SpaceRepresentation will use the Pathfinder to create a FlowField, representing the best trajectories to reach the destination from any point of the space.

Finally, a Piloter module will control the drone as it moves through the cells.







# Credits

MIT license.

quentin.ferre@gmail.com