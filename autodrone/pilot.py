# Tello modules
import djitellopy as dtp

from autodrone.base.mathutils import (
    project_on_plane,
    euclidian_distance,
    vector_to_euler,
)

from mathutils import Vector


class DronePiloter:
    """
    Class responsible for translating directions (given as a velocity vector)
    into actual instructions for the drone.

    Use the Tello drone for a proof of concept : https://github.com/damiafuentes/DJITelloPy
    The Tello must be on the same WiFi as the computer running this code !

    See https://github.com/damiafuentes/DJITelloPy/blob/master/examples/manual-control-pygame.py for source example
    """

    def __init__(self, starting_position: Vector = None, debug_mode=False):
        """_summary_

        Args:
            starting_position (Vector, optional): _description_. Defaults to None.
            debug_mode (bool, optional): debug_mode (bool, optional): If True, commands are not sent but simply printed. Defaults to False.
        """
        self.debug_mode = debug_mode

        if not self.debug_mode:
            # Connect to the Tello if not in debug mode
            self.drone = dtp.Tello()
            self.drone.connect()

            print("Connected to Drone")
        else:
            print("DEBUG MODE WITHOUT DRONE")

        # What are my position and rotation ?
        # TODO Find a way to deduce those, or set them at startup.
        if starting_position is None:
            self.position = self.infer_position()
        else:
            self.position = starting_position
        self.rotation_euler = Vector((0, 0, 0))  # Assume we start on the plane

    def takeoff(self):
        self.drone.takeoff()

    def land(self):
        self.drone.land()

    def infer_position(self):
        # TODO : use cross-view matching to deduce my potential position, or simply use the GNSS chip.
        raise NotImplementedError

    def update_position(self, dx, dy, dz, rotation):
        self.position.x += dx
        self.position.y += dy
        self.position.z += dz
        self.rotation_euler.z += rotation

    def send_instructions(self, desired_velocity: Vector, speed=100, debug_mode=False):
        """Makes the drone move along the specified velocity vector at the desired speed.

        Args:
            desired_velocity (Vector): The desired velocity vector.
            speed (int, optional): Speed in cm/s. Defaults to 100.

        Returns:
            Tuple of (dx, dy, dz, rotation)

            dx, dy, dz : expected delta in centimeters per second along the axes
            rotation : rotation in radians that was applied
        """
        normalized_desired_orientation = desired_velocity.normalized()

        # First orient towards the velocity vector (only for yaw)
        desired_orientation = vector_to_euler(
            normalized_desired_orientation  # , origin=(0, 0, -1)
        ).z

        rotation = self.rotation_euler.z - desired_orientation
        if not self.debug_mode:
            if rotation > 0:
                self.drone.rotate_counter_clockwise(rotation)
            else:
                self.drone.rotate_clockwise(rotation)

        # Then apply the velocity using height and pitch
        # We will almost never use roll (left-right velocity) manually, nor
        # yaw (we already rotated in the previous step).

        # Project on xy plane
        # TODO Do i really need that if I already have x,y,z components ?
        projected_on_xy_plane = project_on_plane(
            desired_velocity,
            normal=Vector((0, 0, 1)),
        )

        # DEBUG : FOR NOW, SIMPLY PRINT THE COMMAND BEING GIVEN INSTEAD OF SENDING IT
        if not self.debug_mode:
            self.drone.send_rc_control(
                left_right_velocity=0,
                forward_back_velocity=euclidian_distance(projected_on_xy_plane) * speed,
                up_down_velocity=desired_velocity.z * speed,
                yaw_velocity=0,
            )

        dx = projected_on_xy_plane.x * speed
        dy = projected_on_xy_plane.y * speed
        dz = desired_velocity.z * speed

        print(f"MOVEMENT ORDER GIVEN FOR: dx {dx} dy {dy} dz {dz} rotation {rotation}")

        # return the expected delta in centimeters per second
        return dx, dy, dz, rotation
