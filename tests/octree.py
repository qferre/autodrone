import sys

sys.path.append("..")  # If called from tests directory
sys.path.append(".")  # If called from main directory

from autodrone.base.octree import OctreeNode, Octree
from mathutils import Vector

# Test subdivision
x = OctreeNode(id=1, center=Vector((0, 0, 0)), size=10)
x.subdivide()


assert set([tuple(n.center) for n in x.children]) == set(
    [
        (-2.5, -2.5, -2.5),
        (-2.5, -2.5, 2.5),
        (-2.5, 2.5, -2.5),
        (-2.5, 2.5, 2.5),
        (2.5, -2.5, -2.5),
        (2.5, -2.5, 2.5),
        (2.5, 2.5, -2.5),
        (2.5, 2.5, 2.5),
    ]
)


# Test distance
t = Octree((0, 0, 0), 10, 10)
t.root.subdivide()
closenode = t.get_closest_cell_to_position((2.5, 2.5, 2.5))
assert tuple(closenode.center) == (2.5, 2.5, 2.5)
assert len(t.get_all_cells(leaf_nodes_only=True)) == 8


graph = t.to_graph(dist_threshold=100, top_k_neighbors=999)
