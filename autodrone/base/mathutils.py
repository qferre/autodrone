import numpy as np
from mathutils import Vector
import bpy


def project_on_xy_plane():
    raise NotImplementedError


def euclidian_distance(a: tuple, b: tuple):
    d = np.array(a) - np.array(b)
    return np.sum(d**2)


def vector_to_euler(vector: Vector):
    # Blender's default orientation is -Z
    return vector.to_track_quat("-Z").to_euler()


def blender_create_cube(center, edge_size, name="Cube"):
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
