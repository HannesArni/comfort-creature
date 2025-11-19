import math

from geometry import GlobalPose, LocalCoordinate
from geometry.rotate_pose_around_coord import rotate_pose_around_coord
from motors.parse_encoder_line import EncoderReading
from utils.constants import CM_PER_TICK, MotorSide


def transform_on_encoder(
    reading: EncoderReading,
    current_pose: GlobalPose,
    left_motor_pos: LocalCoordinate,
    right_motor_pos: LocalCoordinate,
) -> GlobalPose:
    """
    Update the robot's global pose based on an encoder reading.

    Args:
        reading: The encoder reading from one motor.
        current_pose: The robot's current global pose.
        left_motor_pos: The left motor's position in local coordinates.
        right_motor_pos: The right motor's position in local coordinates.

    Returns:
        Updated global pose after applying the encoder reading.
    """
    distance_between_motors = right_motor_pos.distance_to(left_motor_pos)
    if reading.motor == MotorSide.LEFT:
        # Assuming only one tick at a time
        theta = math.atan(CM_PER_TICK / distance_between_motors)
        right_motor_global_position = right_motor_pos.to_global(current_pose)
        new_pose = rotate_pose_around_coord(
            current_pose, right_motor_global_position, -theta
        )
    elif reading.motor == MotorSide.RIGHT:
        # Assuming only one tick at a time
        theta = math.atan(CM_PER_TICK / distance_between_motors)
        left_motor_global_position = left_motor_pos.to_global(current_pose)
        new_pose = rotate_pose_around_coord(
            current_pose, left_motor_global_position, theta
        )
    else:
        new_pose = current_pose  # No change if motor side is unknown

    return new_pose
