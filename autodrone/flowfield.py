import math

from autodrone.base.octree import Octree, OctreeNode
from autodrone.pathfind import Pathfinder
from autodrone.base.mathutils import blender_create_cube, vector_to_euler

# Blender modules
import bpy
from mathutils import Vector

# --------------------- Flowfield, a special octree



class OctreeVectorNode(OctreeNode):

    def __init__(self, id, center:Vector, size:int):
        """Like an OctreeNode, but can also store a vector, and check if it is occupied.

        Args:
            id (_type_): _description_
            center (Vector): _description_
            size (int): _description_
        """
        super().__init__(id, center, size)
        self.vector = Vector((0, 0, 0)) # Vector stored by the OctreeVectorNode and which gives it its name
        self._is_occupied = None  # Flag to indicate if this node is occupied by an obstacle. None at first if never evaluated

    @property
    def is_occupied(self):
        return self._is_occupied

    @is_occupied.setter
    def is_occupied(self, value: object):
        self._is_occupied = value

    def __str__(self) -> str:
        return super().__str__() + f", is occupied {self.is_occupied}"



class FlowField(Octree):
    def __init__(self, root_center, root_size, max_depth=13):
        super().__init__(root_center, root_size, max_depth, node_class=OctreeVectorNode)

    def populate_self(
        self,
        endpos,
        pathfinder: Pathfinder,
        dist_threshold_graph_conversion=1000,
        top_k_neighbors_graph_conversion=8,
    ):

        # Turn the octree into a graph once and for all
        print("Graphing...")
        scene_graph = self.to_graph(
            dist_threshold=dist_threshold_graph_conversion,
            top_k_neighbors=top_k_neighbors_graph_conversion,
        )
        print("Done.")

        print(scene_graph)

        # import networkx as nx

        # A = nx.nx_agraph.to_agraph(scene_graph)  # convert to a graphviz graph
        # A.write("k5.dot")  # write to dot file
        # A.draw("k5.png", prog="neato")
        # assert False

        for cell in self.get_all_cells():
            print("NEW CELL")
            path = pathfinder.pathfind(
                scene_octree=self,
                scene_graph=scene_graph,
                startpos=cell.center,
                endpos=endpos,
            )

            print("PATH", path)

            # The vector is the first vector of the path to to the destination
            if len(path) > 1:
                next_cell = self.get_cell_by_name(path[1])
                dx = next_cell.center.x - cell.center.x
                dy = next_cell.center.y - cell.center.y
                dz = next_cell.center.z - cell.center.z
            else:
                dx, dy, dz = 0, 0, 0

            cell.vector = Vector((dx, dy, dz))
            print(cell.vector)

    def produce_visualisation(self, visibility_scale_factor=0.5):
        for cell in self.get_all_cells(leaf_nodes_only=True):
            empty = bpy.data.objects.new(name="new empty", object_data=None)
            bpy.context.collection.objects.link(empty)
            empty.empty_display_type = "SINGLE_ARROW"

            empty.location = cell.center
            empty.scale = (
                -1 * visibility_scale_factor,
                -1 * visibility_scale_factor,
                -1 * visibility_scale_factor,
            )  # (1, 1, vector_norm(cell.vector))
            empty.rotation_euler = vector_to_euler(cell.vector)
            print(empty.rotation_euler)

        # NOTE : This code does not delete the visual representations yet


