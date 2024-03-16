import networkx as nx


class Pathfinder:
    @staticmethod
    def pathfind(
        scene_octree,
        scene_graph,
        startpos,
        endpos,
    ):
        """Tries to find a path in the given scene between startpos and endpos.
        Uses the A-star algorithm.

        Args:
            scene_octree (_type_): _description_
            scene_graph (_type_): _description_
            startpos (_type_): _description_
            endpos (_type_): _description_

        Returns:
            _type_: _description_
        """
        path = []
        start_cell = scene_octree.get_closest_cell_to_position(startpos)
        assert (
            start_cell.outgoing_graph_edges > 0
        ), f"Trying to path from a cell without outgoing graph edges : {start_cell}"

        # Move from startpos to start_cell.center
        # path += [Vector(
        #     start_cell.center.x - startpos.x,
        #     start_cell.center.y - startpos.y,
        #     start_cell.center.z - startpos.z,
        # )]

        # Complete path to end cell
        end_cell = scene_octree.get_closest_cell_to_position(endpos)
        assert (
            end_cell.outgoing_graph_edges > 0
        ), f"Trying to path into a cell without outgoing graph edges : {end_cell}"

        print(f"PATHING FROM {start_cell} TO {end_cell}")

        try:
            path += nx.astar_path(
                scene_graph,
                start_cell.id,
                end_cell.id,
                weight="weight",
            )
        except:
            # Well, if there is no path, just return an empty path.
            # This usually happens if you are evaluating a cell that is in an
            # "island", meaning it has neighbors but is not connected to the
            # destination.
            print("NO PATH EXISTS.")

        return path

    def local_avoidance_behavior(self, desired_path_vector):
        """
        # TODO : before implementing ORCA or depth estimation. Just stop if there is an obstacle at 1 m
        obstacle = raytrace_blender(desired_path_vector, max_distance=1m)
        if obstacle:
            return Vector(0, 0, 0)
        """

        return desired_path_vector
