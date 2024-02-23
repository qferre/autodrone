"""
This must be run within Blender !
TODO : blender interpreter by default has its workdir in the home dir when run from within Blender interface
"""

import sys
from pathlib import Path
import time
from autodrone.utils import ArgumentParserForBlender

sys.path.append(".")  # necessary to import script from the blender python interpreter

from autodrone.space import SpaceRepresentation
from autodrone.pathfind import DronePiloter, Pathfinder

# from autodrone.main import update
from autodrone.llm import LLMAgent

# Blender modules
import bpy
from mathutils import Vector


# Argparser
parser = ArgumentParserForBlender()
parser.add_argument("-sp", "--start_pos", type=str, required=True, help="")
args = parser.parse_args()

start_position = args["start_pos"]


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
drone_piloter = DronePiloter(starting_position = start_position)


# ------------------------ Command interpretation ---------------------------- #
# TODO  integrate the LLM module to translate input command into a position

user_input = input("Please enter your instructions: ")

# Continue the code after Enter is pressed
print(f"You said : {user_input}. Your request will now be processed.")
# target = LLMAgent(
#     user_input
# )
# Default to pre-set for now
navigator = bpy.object["Navigator"]
target = bpy.objects["Target"]

# TODO : the start position, for now, will be specified by command line I think.
# The different query positions will be given in an index, and the LLM will just fetch the appropriate ones from this index.
# The path of the index should be an argument of the command line

# ----------------------------- Pathfinding ---------------------------------- #
# Now that we have the targets, compute the paths and populate the flowfield.
scene.octree.populate_self(navigator.position, target.postion, pathfinder)
# In theory, as long as the target does not change, we do not need to recompute
# the paths even if the starting position changes (that's the entire point of
# the flowfield).

destination_cell = scene.octree.get_closest_cell_to_position(target.position)

# ------------------------------ Piloting ------------------------------------ #
stop = False
start_time = time.time()
while not stop:
    # The main pathfiding relies on the scene cartography obtained by photogrammetry.
    # We use it to get a velocity vector towards next waypoint. Then, we combine
    # it with a local avoidance which corrects this vector to ensure we don't
    # bump into anything.
    """
    The info for local avoidance is given only by DPT, I think ; I don't think
    we need to update the scene represetnation by adding obstacls unless they
    are massive, new, and immobile, otherwise
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
    # We maintain the instruction for one entire second (TODO reduce this likely)
    # Each step, we get the estimated dx dy dz in cm/s
    COMMAND_MAINTAIN_TIME = 1
    SPEED = 50
    piloting_start_time = time.time()
    while order_time <= piloting_start_time + COMMAND_MAINTAIN_TIME:
        order_time = time.time()
        dx, dy, dz = drone_piloter.send_instructions(final_vector_velocity, speed=SPEED)

    # Update our estimated position based on our speed
    # Recall that the speed was given in cm/s in the vector (as per DJiTelloPy's doc), and
    # that we update the position every second, so we just divide by 100
    drone_piloter.update_position(dx=dx / 100, dy=dy / 100, dz=dz / 100)

    # If we have arrived at our destination, stop
    current_closest_cell = scene.octree.get_closest_cell_to_position(
        drone_piloter.position
    )
    if current_closest_cell == destination_cell:
        stop = True

    # If we have timed out, stop
    TIMEOUT = 60
    if time.time() > start_time + TIMEOUT:
        stop = True
