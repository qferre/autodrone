from autodrone.flowfield import FlowField, OctreeVectorNode
from mathutils import Vector


class SpaceRepresentation:
    """
    When created from within a Blender environment, will create an octree
    representation of the scene.
    """

    def __init__(
        self,
        origin_vector=Vector((0, 0, 5)),
        scene_diameter=10,
        max_depth_flowfield=4,
    ):
        """_summary_

        Args:
            origin_vector (_type_, optional): _description_. Defaults to Vector((0, 0, 5)) which representes center of the scene at 5m of height.
            scene_diameter (int, optional): _description_. Defaults to 10.
            max_depth_flowfield (int, optional): _description_. Defaults to 4.
        """

        ## CREATE THE REPRESENTATION
        # Completely fill the space around me with an octree, and subdivide it when needed
        self.octree = FlowField(
            # The root cell encompasses the entire scene
            root_center=origin_vector,
            root_size=scene_diameter,
            max_depth=max_depth_flowfield,
        )
        self._subdivide_flowfield(self.octree)

    @staticmethod
    def _subdivide_flowfield(flowfield: FlowField):
        """
        For the given flowfield, will recursively subdivide each cell if it has
        not been divided before (ie. has no child cells).
        """
        depth = 0
        while depth < flowfield.max_depth:
            current_cells = flowfield.get_all_cells(leaf_nodes_only=False)
            print(f"DIVIDING, {len(current_cells)}")
            for cell in current_cells:
                print(f"DIV {cell}")
                if cell.children is None:
                    cell.subdivide(node_class=OctreeVectorNode)
            depth += 1
