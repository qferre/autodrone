import sys

sys.path.append("..")

from autodrone.base.octree import OctreeNode, Octree
from mathutils import Vector

# Test subdivision
x = OctreeNode(id=1, center=Vector((0, 0, 0)), size=10)
x.subdivide()

assert set([n.center for n in x.children]) == set(
    [
        (-5.0, -5.0, -5.0),
        (-5.0, -5.0, 5.0),
        (-5.0, 5.0, -5.0),
        (-5.0, 5.0, 5.0),
        (5.0, -5.0, -5.0),
        (5.0, -5.0, 5.0),
        (5.0, 5.0, -5.0),
        (5.0, 5.0, 5.0),
    ]
)


# Test distance
t = Octree((0, 0, 0), 10, 10)
t.root.subdivide()
closenode = t.get_closest_cell_to_position((5, 5, 5))
assert closenode.center == (5.0, 5.0, 5.0)
assert len(t.get_all_cells(leaf_nodes_only=True)) == 8


graph = t.to_graph(dist_threshold=100, top_k_neighbors=999)
