import asyncio
import logging
from interface_stubs import Encoder, MicroSwitch, Motor
from exceptions import InvalidDirectionError, InvalidDistanceError


# Constants
VALID_DIRECTIONS = [1, 2]
MOTOR_MOVEMENT_DEGREES_PER_DISTANCE_UNIT = 20
MOTOR_MOVEMENT_DEGREES_PER_ENCODER_FLIP = 5
EXPECTED_TIME_FOR_ENCODER_FLIP = 0.1

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Arm:
    """
    Class to control the arm movement based on the provided direction and distance.
    """

    def __init__(self, motor: Motor, encoder: Encoder, microswitch: MicroSwitch):
        self._motor = motor
        self._encoder = encoder
        self._microswitch = microswitch

    @staticmethod
    def _validate_input(direction: int, distance: int):
        """
        Validates the input for direction and distance.

        :param direction: Direction to move the arm (1 for left, 2 for right).
        :param distance: Distance to move the arm (in units).
        :raises InvalidDirectionError: If the direction is invalid.
        :raises InvalidDistanceError: If the distance is invalid.
        """
        if distance < 1 or distance % 1 != 0:
            # Assuming a fraction is not valid to make a consistent behaviour
            raise InvalidDistanceError(f"Invalid distance: {distance}, should be a natural positive number")
        if direction not in VALID_DIRECTIONS:
            raise InvalidDirectionError(f"Invalid direction: {direction}, Valid directions are: left (1) or right (2)")
    async def move_arm(self, direction: int, distance: int) -> None:
        """
        Moves the arm in the specified direction for the given distance.

        :param direction: Direction to move the arm (1 for left, 2 for right).
        :param distance: Distance to move the arm (in units).
        """
        try:
            self._validate_input(direction, distance)
        except (InvalidDirectionError, InvalidDistanceError) as e:
            logging.error(str(e))
            raise e

        movement_degrees = MOTOR_MOVEMENT_DEGREES_PER_DISTANCE_UNIT * distance
        encoder_flips_needed = movement_degrees // MOTOR_MOVEMENT_DEGREES_PER_ENCODER_FLIP
        encoder_flips_count = 0
        encoder_previous_status = self._encoder.status()

        self._motor.on(direction)

        try:
            while encoder_flips_count < encoder_flips_needed:
                await asyncio.sleep(EXPECTED_TIME_FOR_ENCODER_FLIP / 2)
                # The expected change speed for the encoder is around 10 times a second. To avoid missing slightly
                # faster changes, we will check twice every 0.1 seconds. This might not be the most efficient way,
                # but for the purpose of the exercise, I assumed accuracy was more important than this efficiency
                # difference.

                if self._microswitch.status() == 1:
                    # Assuming that it's allowed for the motor to stay on for a potential 0.05 seconds also after it
                    # reached the end, it should also be allowed to start a motor movement for that period in case
                    # the starting position was at one of the ends and tried to keep moving in that direction
                    logging.info("Stop: MicroSwitch activated.")
                    break

                encoder_current_status = self._encoder.status()
                if encoder_current_status != encoder_previous_status:
                    encoder_flips_count += 1
                encoder_previous_status = encoder_current_status
        except Exception as e:
            logging.error(f"Exception occurred during arm movement: {e}")
        finally:
            self._motor.off()
