import numpy as np
from mathutils import Vector
import bpy

def euclidian_distance(a: tuple, b: tuple):
    d = np.array(a) - np.array(b)
    return np.sum(d**2)


def vector_to_euler(vector: Vector):
    """Converts a 3D Vector to a Euler Quarternion. Blender's default orientation
    is towards -Z, so use this for the conversion.

    Args:
        vector (Vector): Vector to be converted.

    Returns:
        Euler quarternion
    """
    # Blender's default orientation is -Z
    return vector.to_track_quat("-Z").to_euler()


def project_on_plane(vector : Vector, normal: Vector):
    """Project the vector on the plan defined by the normal.

    Args:
        vector (Vector): Vector to be projected.
        normal (Vector): Vector defining the normal of the plane on which we project.
    """
    dot_product = np.dot(normal, vector)
    sub_vector = Vector(dot_product * normal)
    projected_vector = vector - sub_vector
    return projected_vector


def blender_create_cube(center: Vector, edge_size:float, name="Cube"):
    """Creates a cube within the Blender scene with the desired parameters.

    Args:
        center (Vector): Position of the cube center.
        edge_size (float): Length of each edge
        name (str, optional): Name of the object. Defaults to "Cube".

    Returns:
        A reference to the newly created cube in Blender's Python API.
    """
    center = Vector(center)

    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Create vertices and faces for the cube
    verts = [
        center + Vector(c) * edge_size / 2
        for c in [
            (-1, -1, -1),
            (1, -1, -1),
            (-1, 1, -1),
            (1, 1, -1),
            (-1, -1, 1),
            (1, -1, 1),
            (-1, 1, 1),
            (1, 1, 1),
        ]
    ]
    faces = [
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (0, 2, 6, 4),
        (1, 5, 7, 3),
        (0, 4, 5, 1),
        (2, 3, 7, 6),
    ]

    # Create the mesh
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    return obj


def blender_raycast(origin, target, max_distance=None):
    """_summary_

    Args:
        origin (_type_): _description_
        target (_type_): _description_
        max_distance (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    scene = bpy.context.scene
    direction = target - origin
    distance = direction.length
    direction.normalize()

    depsgraph = bpy.context.evaluated_depsgraph_get()

    print("Casting new ray...")

    if max_distance is not None:
        distance = min(distance, max_distance)

    result, location, normal, index, object, matrix = scene.ray_cast(
        depsgraph=depsgraph, origin=origin, direction=direction, distance=distance
    )

    if result:
        return location
    return None
