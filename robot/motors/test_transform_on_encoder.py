import math

from geometry import GlobalCoordinate, GlobalPose, LocalCoordinate
from motors.parse_encoder_line import EncoderReading
from motors.transform_on_encoder import transform_on_encoder
from utils.constants import CM_PER_TICK, MotorSide


def test_left_motor_tick_rotates_around_right_motor():
    """Left motor tick should rotate the pose counterclockwise around right motor."""
    current_pose = GlobalPose(GlobalCoordinate(0, 0), 0)
    left_motor = LocalCoordinate(-10, 0)  # 10 cm to the left
    right_motor = LocalCoordinate(10, 0)  # 10 cm to the right
    reading = EncoderReading(motor=MotorSide.LEFT, is_forward=True, count=1, dt=100)

    result = transform_on_encoder(reading, current_pose, left_motor, right_motor)

    # Calculate expected rotation
    distance = 20  # Distance between motors
    expected_theta = math.atan(CM_PER_TICK / distance)

    # The pose should have rotated counterclockwise (negative rotation as per code)
    assert math.isclose(result.heading, -expected_theta, abs_tol=1e-9)
    # Position should have moved as the left motor advanced
    assert result.position.x != 0 or result.position.y != 0


def test_right_motor_tick_rotates_around_left_motor():
    """Right motor tick should rotate the pose clockwise around left motor."""
    current_pose = GlobalPose(GlobalCoordinate(0, 0), 0)
    left_motor = LocalCoordinate(-10, 0)
    right_motor = LocalCoordinate(10, 0)
    reading = EncoderReading(motor=MotorSide.RIGHT, is_forward=True, count=1, dt=100)

    result = transform_on_encoder(reading, current_pose, left_motor, right_motor)

    # Calculate expected rotation
    distance = 20
    expected_theta = math.atan(CM_PER_TICK / distance)

    # The pose should have rotated clockwise (positive rotation as per code)
    assert math.isclose(result.heading, expected_theta, abs_tol=1e-9)
    # Position should have moved as the right motor advanced
    assert result.position.x != 0 or result.position.y != 0


def test_symmetric_motor_placement():
    """Test with motors symmetrically placed relative to robot center."""
    current_pose = GlobalPose(GlobalCoordinate(5, 5), math.pi / 4)  # 45° heading
    left_motor = LocalCoordinate(-5, 0)
    right_motor = LocalCoordinate(5, 0)
    reading = EncoderReading(motor=MotorSide.LEFT, is_forward=True, count=1, dt=100)

    result = transform_on_encoder(reading, current_pose, left_motor, right_motor)

    # Should produce a valid rotation
    distance = 10
    expected_rotation = math.atan(CM_PER_TICK / distance)
    expected_heading = current_pose.heading - expected_rotation

    assert math.isclose(result.heading, expected_heading, abs_tol=1e-9)


def test_unknown_motor_side_returns_unchanged():
    """Unknown motor side should return the pose unchanged."""
    current_pose = GlobalPose(GlobalCoordinate(3, 4), math.pi / 6)
    left_motor = LocalCoordinate(-10, 0)
    right_motor = LocalCoordinate(10, 0)
    # Create reading with invalid motor side
    reading = EncoderReading(motor=None, is_forward=True, count=1, dt=100)

    result = transform_on_encoder(reading, current_pose, left_motor, right_motor)

    assert result.position.x == current_pose.position.x
    assert result.position.y == current_pose.position.y
    assert result.heading == current_pose.heading
