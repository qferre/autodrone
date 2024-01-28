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

        # Move from startpos to start_cell.center
        # path += [Vector(
        #     start_cell.center.x - startpos.x,
        #     start_cell.center.y - startpos.y,
        #     start_cell.center.z - startpos.z,
        # )]

        # Complete path to end cell
        end_cell = scene_octree.get_closest_cell_to_position(endpos)
        path += nx.astar_path(
            scene_graph,
            start_cell.id,
            end_cell.id,
            weight="weight",
        )

        return path

    def local_avoidance_behavior(desired_path_vector, scene):
        # Based on http://gamma.cs.unc.edu/ORCA/publications/ORCA.pdf

        # Calculate all velocities that would cause the agent to collide with an obstacle (probably a function inside SpaceRepresentation)
        # Then use gradient descent to find the highest velocity (closest to pathing vector) that does not conflict

        # TODO : may require adaptation for drones since ORCA is not designed for actors with lots of inertia

        # For now, it's not needed for the proof of concept. Just return the real vector.
        return desired_path_vector
