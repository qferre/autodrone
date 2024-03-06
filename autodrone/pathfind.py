import networkx as nx


class Pathfinder:
    @staticmethod
    def pathfind(
        scene_octree,
        scene_graph,
        startpos,
        endpos,
    ):
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
        # Based on http://gamma.cs.unc.edu/ORCA/publications/ORCA.pdf

        # Calculate all velocities that would cause the agent to collide with an obstacle (probably a function inside SpaceRepresentation)
        # Then use gradient descent to find the highest velocity (closest to pathing vector) that does not conflict

        # TODO : may require adaptation for drones since ORCA is not designed for actors with lots of inertia

        # For now, it's not needed for the proof of concept. Just return the real vector.

        """
        # TODO : before implementing ORCA or depth estimation. Just stop if there is an obstacle at 1 m
        obstacle = raytrace_blender(desired_path_vector, max_distance=1m)
        if obstacle:
            return Vector(0, 0, 0)
        """

        return desired_path_vector
