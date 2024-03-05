import sys

sys.path.append(".")

from autodrone.pilot import DronePiloter

from mathutils import Vector


desired_velocity = Vector((5, 4, 1))
start_position = Vector((0, 0, 5))


piloter_entity = DronePiloter(
    debug_mode=True,  # Text only, do not attempt to connect to the drone
    starting_position=start_position,
)

dx, dy, dz, rotation = piloter_entity.send_instructions(
    desired_velocity,
    speed=100,
)

# Update our estimated position based on our speed in cm/s
piloter_entity.update_position(dx=dx / 100, dy=dy / 100, dz=dz / 100, rotation=rotation)


new_position = piloter_entity.position
new_rotation = piloter_entity.rotation_euler

print(f"New position {new_position}, new rotation {new_rotation}")
assert new_position == Vector(
    (
        start_position.x + dx / 100,
        start_position.y + dy / 100,
        start_position.z + dz / 100,
    )
)

assert new_rotation == (0, 0, 0 + rotation)
