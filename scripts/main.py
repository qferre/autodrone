"""
This must be run within Blender !
TODO : blender interpreter by default has its workdir in the home dir when run from within Blender interface
"""

import sys
from pathlib import Path
import time

sys.path.append(".")  # necessary to import script from the blender python interpreter

from autodrone.space import SpaceRepresentation
from autodrone.pathfind import DronePiloter, Pathfinder

# from autodrone.main import update
from autodrone.llm import LLMAgent

# Blender modules
import bpy
from mathutils import Vector


# Before beginning, assert that we are inside a Blender environment, and that
# there is a mesh representing the real environment available.
# TODO assert mesh exists


# ------------------- Initialize modules and representation ------------------ #

# Create a SpaceRepresentaiton based on the currently open Blender file (the file with which the script was called)
scene = SpaceRepresentation() 
# NOTE If the scene changes (new obstacles, ...) the SpaceRepresentation must
# be updated.

# Initialize modules
pathfinder = Pathfinder()
drone_piloter = DronePiloter()


# ------------------------ Command interpretation ---------------------------- #
# TODO  integrate the LLM module to translate voice commands into a position
# target = LLMAgent(
#     voice_input
# )
# Default to pre-set for now
navigator = bpy.object["Navigator"]
target = bpy.objects["Target"]


# ----------------------------- Pathfinding ---------------------------------- #
# Now that we have the targets, compute the paths and populate the flowfield.
scene.octree.populate_self(navigator.position, target.postion, pathfinder)
# In theory, as long as the target does not change, we do not need to recompute
# the paths even if the starting position changes (that's the entire point of
# the flowfield).

# ------------------------------ Piloting ------------------------------------ #
stop = False
while not stop:
    # The main pathfiding relies on the scene cartography obtained by photogrammetry.
    # We use it to get a velocity vector towards next waypoint. Then, we combine
    # it with a local avoidance which corrects this vector to ensure we don't
    # bump into anything.
    """
    The info for local avoidance is given only by DPT, I think ; I don't think we need to update the scene represetnation by adding obstacls unless they are massive, new, and immobile, otherwise
    """

    # My pathing_vector is the vector (in the flowfield) of the cell I am
    # currently standing inside of.
    closest_cell = scene.octree.get_closest_cell_to_position(
        drone_piloter.position
    )  # TODO closest, or inside ?
    pathing_vector = closest_cell.vector

    # Apply local avoidance behavior to edit the pathing_vector
    final_vector_velocity = pathfinder.local_avoidance_behavior(
        desired_path_vector=pathing_vector, scene=scene
    )

    # Finally, instruct the drone piloter to move at this velocity
    drone_piloter.send_instructions(final_vector_velocity)
    time.sleep(0.1)
