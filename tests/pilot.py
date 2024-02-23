piloter_entity = DronePiloter()

desired_velocity = Vector(5, 4, 1)
start_position = Vector(0, 0, 5)


dx, dy, dz = piloter_entity.send_instructions(
    desired_velocity, speed=60, debug_mode=True  # Text only
)

# Update our estimated position based on our speed in cm/s
piloter_entity.update_position(dx=dx / 100, dy=dy / 100, dz=dz / 100)


new_position = piloter_entity.position

assert new_position == Vector(
    start_position.x + dx / 100,
    start_position.y + dy / 100,
    start_position.z + dz / 100,
)
