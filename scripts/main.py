import sys

sys.path.append(".")  # necessary to import script from the blender python interpreter
sys.path.append("..")


from pathlib import Path
import time
from autodrone.utils import ArgumentParserForBlender


from autodrone.space import SpaceRepresentation
from autodrone.pilot import DronePiloter
from autodrone.pathfind import Pathfinder

# from autodrone.main import update
from autodrone.llm import RAG_LLMAgent

# Blender modules
try:
    import bpy
    from mathutils import Vector
except ImportError:
    raise ImportError(
        "Cannot find Blender modules. Did you run this script using the Blender Python interpreter?"
    )

# Argparser
parser = ArgumentParserForBlender()
parser.add_argument("-sp", "--start_pos", type=str, required=True, help="")
args = parser.parse_args()


start_position = Vector((float(i) for i in args.start_pos.split(",")))
print(f"Start position: {start_position}")


# Before beginning, assert that we are inside a Blender environment, and that
# there is a mesh representing the real environment available.
# TODO assert mesh exists


# ------------------- Initialize modules and representation ------------------ #

# Create a SpaceRepresentation based on the currently open Blender file (the
# file with which the script was called).
scene = SpaceRepresentation(max_depth_flowfield=3)
# NOTE If the scene changes (new obstacles, ...) the SpaceRepresentation must
# be updated.


# ------------------------ Command interpretation ---------------------------- #
# TODO  integrate the LLM module to translate input command into a position

"""
llm_rag_agent = RAG_LLMAgent(
    model_name="mistralai/Mistral-7B-Instruct-v0.2", prompt_template_key="drone_loc"
)
index = Path(args.index_path).read_text()
llm_rag_agent.setup_retriever_for_this_context(text=index)
"""

user_input = input("Please enter your instructions: ")
# Continue the code after Enter is pressed
print(f"You said: {user_input}. Your request will now be processed.")

# target = llm_rag_agent(question=user_input)
# Default to pre-set for now
navigator = bpy.data.objects["Navigator"]
target = bpy.data.objects["Destination"]
start_position = navigator.location

# TODO : the start position, for now, will be specified by command line I think.
# The different query positions will be given in an index, and the LLM will just fetch the appropriate ones from this index.
# The path of the index should be an argument of the command line

# ----------------------------- Pathfinding ---------------------------------- #

# Initialize modules
pathfinder = Pathfinder()
drone_piloter = DronePiloter(
    starting_position=start_position,  ### aaaaaa
    debug_mode=True,  # DO NOT KEEP THIS
)

# Now that we have the targets, compute the paths and populate the flowfield.
scene.octree.populate_self(
    endpos=target.location, pathfinder=pathfinder, top_k_neighbors_graph_conversion=8
)
scene.octree.produce_visualisation()


# In theory, as long as the target does not change, we do not need to recompute
# the paths even if the starting position changes (that's the entire point of
# the flowfield).

destination_cell = scene.octree.get_closest_cell_to_position(target.location)


# ------------------------------ Piloting ------------------------------------ #
stop = False
start_time = time.time()

drone_piloter.takeoff()

while not stop:
    print("Main loop...")
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

    print(f"Current pathing vector {pathing_vector} from cell {closest_cell}")

    # Apply local avoidance behavior to edit the pathing_vector
    final_vector_velocity = pathfinder.local_avoidance_behavior(
        desired_path_vector=pathing_vector
    )

    # Finally, instruct the drone piloter to move at this velocity
    # We maintain the instruction for one entire second
    # Each step, we get the estimated dx dy dz in cm/s
    COMMAND_MAINTAIN_TIME = 1
    SPEED = 100
    piloting_start_time = order_time = time.time()

    order_time = time.time()
    dx, dy, dz, rotation = drone_piloter.send_instructions(
        final_vector_velocity, speed=SPEED
    )
    time.sleep(
        COMMAND_MAINTAIN_TIME
    )  # Maintain the current command for COMMAND_MAINTAIN_TIME

    print(f"dx {dx}, dy {dy}, dz {dz}, rotation {rotation}")

    # Update our estimated position based on our speed
    # Recall that the speed was given in cm/s in the vector (as per DJiTelloPy's doc), and
    # that we update the position every second, so we just divide by 100
    # 100 cm in a meter, multiplied by one second (by default the command maintain time is one second)
    drone_piloter.update_position(
        dx=dx / 100 * COMMAND_MAINTAIN_TIME,
        dy=dy / 100 * COMMAND_MAINTAIN_TIME,
        dz=dz / 100 * COMMAND_MAINTAIN_TIME,
        rotation=rotation,
    )
    dx, dy, dz, rotation = 0, 0, 0, 0  # Reset memorized movement

    # If we have arrived at our destination, stop
    current_closest_cell = scene.octree.get_closest_cell_to_position(
        drone_piloter.position
    )

    print(f"Current cell {current_closest_cell} -> Destination {destination_cell}")

    if current_closest_cell == destination_cell:
        stop = True
        print("Destination reached.")

    # If we have timed out, stop
    TIMEOUT = 60
    if time.time() > start_time + TIMEOUT:
        stop = True
        print("Timed out.")


# Stop the drone and tell it to land
drone_piloter.send_instructions(Vector((0, 0, 0)), speed=0)
drone_piloter.land()
