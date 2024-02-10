"""
This test must be run in the Blender interpret, using the scenes/basic.blend scene.
The Makefile will take care of it.
"""

import sys

sys.path.append(".")

from autodrone.space import SpaceRepresentation
from autodrone.pathfind import Pathfinder
import bpy

space = SpaceRepresentation(max_depth_flowfield=3)
print(f"CREATED with nodes: {len(space.octree.get_all_cells(leaf_nodes_only=True))}")


space.octree.populate_self(
    endpos=bpy.data.objects["Destination"].location,
    pathfinder=Pathfinder(),
    dist_threshold_graph_conversion=100,
    top_k_neighbors_graph_conversion=15,
)
space.octree.produce_visualisation()
