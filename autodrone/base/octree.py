import networkx as nx
from autodrone.base.mathutils import euclidian_distance
from mathutils import Vector
from autodrone.base.mathutils import blender_raycast


class OctreeNode:
    def __init__(self, id: str, center: Vector, size: float):
        """_summary_

        Each node is a CUBE, not a SPHERE !

        Args:
            id (str): need a unique id for later
            center (Vector): The center point of the node
            size (float): The size (side length) of the node
        """

        self.id = id
        self.center = center
        self.size = size

        self.children = None

        self.outgoing_graph_edges = 0

    def __str__(self) -> str:
        return f"Octree Node {self.id}, center {self.center}, size {self.size}, children {self.children}, outgoing_graph_edges {self.outgoing_graph_edges}"

    def subdivide(self, node_class=None):
        """Subdivide the node into eight child nodes

        Args:
            node_class (_type_, optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
        """

        if node_class is None:
            node_class = OctreeNode
        if self.children is None:
            self.children = list()

            # Subdivide the node into eight child nodes
            child_size = self.size / 2
            xc, yc, zc = self.center

            x_centers = [xc - self.size / 4, xc + self.size / 4]
            y_centers = [yc - self.size / 4, yc + self.size / 4]
            z_centers = [zc - self.size / 4, zc + self.size / 4]

            child_id = 0
            for i in x_centers:
                for j in y_centers:
                    for k in z_centers:
                        self.children.append(
                            node_class(
                                id=f"{self.id}-{child_id}",
                                center=Vector((i, j, k)),
                                size=child_size,
                            )
                        )

                        child_id += 1

        else:
            raise ValueError("Cannot subdivide a node which already has children.")


class Octree:
    def __init__(self, root_center:Vector, root_size:float, max_depth=13, node_class=OctreeNode):
        """_summary_

        Args:
            root_center (Vector): _description_
            root_size (float): _description_
            max_depth (int, optional): _description_. Defaults to 13.
            node_class (_type_, optional): _description_. Defaults to OctreeNode.
        """
        self.root = node_class(center=root_center, size=root_size, id="root")
        self.max_depth = max_depth

    def to_graph(self, dist_threshold:float, top_k_neighbors:int):
        """
        Turn this into a networkx graph,
        NOTE this is done so I can use A Star which is integrated in networkx

        Args:
            dist_threshold (float): _description_
            top_k_neighbors (int): _description_

        Returns:
            _type_: _description_
        """
        # remove cells with children (ie. take only leaf nodes)
        # then just take neighboring cells and add a link between them

        G = nx.Graph()
        for cell in self.get_all_cells(leaf_nodes_only=True):
            neighbours = self.get_neighbours_of_cell(cell, dist_threshold)

            # Keep only top k neighbors which are closest
            neighbours_weighted = {
                n: euclidian_distance(cell.center, n.center) for n in neighbours
            }
            neighbours_sorted = sorted(
                neighbours_weighted.items(), key=lambda x: x[1], reverse=False
            )

            neighbours_final = [i[0] for i in neighbours_sorted[:top_k_neighbors]]

            # Record amount of outgoing edges
            cell.outgoing_graph_edges = 0

            for n in neighbours_final:

                # Disallow moving into an occupied cell, and disallow the movement
                # if a ray trace shows we would cross something.
                ray_is_blocked_at_this_position = blender_raycast(cell.center, n.center)
                print(f"BLOCKING {ray_is_blocked_at_this_position}")

                if ray_is_blocked_at_this_position is None:
                    print("Adding....")
                    G.add_edge(
                        cell.id,
                        n.id,
                        weight=euclidian_distance(
                            cell.center, n.center
                        ),  # Plus the edge weight which is the distance
                    )

                    cell.outgoing_graph_edges += 1
        return G

    def get_all_cells(self, leaf_nodes_only=False):
        all_nodes = []
        all_nodes.append(self.root)  # Remember to add the root !

        def return_children(n, all_nodes):
            if n.children is not None:
                for c in n.children:
                    all_nodes.append(c)
                    return_children(c, all_nodes)

            all_nodes = list(
                set(all_nodes)
            )  # Ensure no duplicates (should never happen, but just in case)

        return_children(self.root, all_nodes)

        if leaf_nodes_only:
            for n in all_nodes:
                if n.children is not None:
                    all_nodes.remove(n)

        return all_nodes

    def get_cell_by_name(self, id: str):
        for cell in self.get_all_cells():
            if cell.id == id:
                return cell
        return None

    def get_closest_cell_to_position(self, pos: tuple, leaf_nodes_only=True):
        min_dist = float("inf")
        output = self.root
        for cell in self.get_all_cells(leaf_nodes_only=leaf_nodes_only):
            dist = euclidian_distance(pos, cell.center)
            if dist < min_dist:
                output = cell
                min_dist = dist
        return output

    def get_neighbours_of_cell(self, cell, dist_threshold):
        # get top K cells which are closest to cell's center but are not the cell
        # return them
        result = []
        for candidate in self.get_all_cells(leaf_nodes_only=True):
            dist = euclidian_distance(candidate.center, cell.center)
            if dist != 0 and dist <= dist_threshold:
                result.append(candidate)

        if len(result) == 0:
            raise ValueError(
                "No neighbors were found. Your dist_threshold must be too low for the scene considered."
            )

        return result
