# Tello modules
import djitellopy as dtp


class DronePiloter:
    """
    Class responsible for translating directions (given as a velocity vector)
    into actual instructions for the drone.

    Use the Tello drone for a proof of concept : https://github.com/damiafuentes/DJITelloPy

    See https://github.com/damiafuentes/DJITelloPy/blob/master/examples/manual-control-pygame.py for source example
    """

    def __init__(self):
        # Connect to the Tello
        self.drone = dtp.Tello()
        self.drone.connect()

        self.position = Vector()
        self.position.x = None
        self.position.y = None
        self.position.z = None

        self.rotation_euler = Vector()
        self.rotation_euler.x = None
        self.rotation_euler.y = None
        self.rotation_euler.z = None

        # What are my position and rotation ?
        # TODO Find a way to deduce those, or set them at startup.
        self.position, self.rotation_euler = self.infer_position()

    def takeoff(self):
        self.drone.takeoff()

    def land(self):
        self.drone.land()

    def infer_position(self):
        # TODO : use cross-view matching to deduce my potential position, or simply use the GNSS chip.
        raise NotImplementedError

    def send_instructions(self, desired_velocity, speed=60):
        normalized_desired_orientation = normalize(desired_velocity)

        # First orient towards the velocity vector (only for yaw)
        desired_orientation = vector_to_euler(normalized_desired_orientation, origin=(0, 0, -1)).z
        rotation = self.rotation_euler.z - desired_orientation

        if rotation > 0:
            self.drone.rotate_counterclockwise(rotation)
        else:
            self.drone.rotate_clockwise(rotation)

        # Then apply the velocity using height and pitch
        # We will almost never use roll (left-right velocity) manually.

        projected_on_xy_plane = project_on_xy_plane(desired_velocity)

        self.drone.send_rc_control(
            left_right_velocity=0,
            forward_back_velocity=euclidean_distance(projected_on_xy_plane) * speed,
            up_down_velocity=normalized_desired_orientation.y * speed,
        )
