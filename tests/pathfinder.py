import sys

sys.path.append("..")

from autodrone.base.octree import OctreeNode, Octree
from autodrone.pathfind import Pathfinder
from mathutils import Vector

# Create a basic grid
t = Octree(root_center=Vector((0, 0, 0)), root_size=10)
t.root.subdivide()
for c in t.root.children:
    c.subdivide()
assert len(t.get_all_cells()) == 1 + 8 + 8 * 8
gridgraph = t.to_graph(dist_threshold=100, top_k_neighbors=999)

# Test pathfinding
path = Pathfinder.pathfind(
    scene_octree=t,
    startpos=Vector((0, 0, 0)),
    endpos=Vector((7.5, 7.5, 7.5)),
    dist_threshold_graph_conversion=100,
)
assert path == ["root-0", "root-0-7", "root-7", "root-7-7"]
