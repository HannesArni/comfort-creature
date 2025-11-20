import math

from geometry import GlobalCoordinate, GlobalPose
from geometry.rotate_pose_around_coord import rotate_pose_around_coord


def test_rotate_90_degrees_counterclockwise():
    """Rotate a point 90 degrees counterclockwise around origin."""
    pose = GlobalPose(GlobalCoordinate(1, 0), 0)
    origin = GlobalCoordinate(0, 0)
    angle = math.pi / 2  # 90 degrees

    result = rotate_pose_around_coord(origin, pose, angle)
    print(result)
    # Point (1, 0) rotated 90° CCW around origin should be at (0, 1)
    assert math.isclose(result.position.x, 0, abs_tol=1e-9)
    assert math.isclose(result.position.y, 1, abs_tol=1e-9)
    assert math.isclose(result.heading, math.pi / 2, abs_tol=1e-9)


def test_rotate_180_degrees():
    """Rotate a point 180 degrees around origin."""
    point = GlobalPose(GlobalCoordinate(1, 0), 0)
    origin = GlobalCoordinate(0, 0)
    angle = math.pi  # 180 degrees

    result = rotate_pose_around_coord(origin, point, angle)

    # Point (1, 0) rotated 180° around origin should be at (-1, 0)
    assert math.isclose(result.position.x, -1, abs_tol=1e-9)
    assert math.isclose(result.position.y, 0, abs_tol=1e-9)
    assert math.isclose(result.heading, math.pi, abs_tol=1e-9)


def test_rotate_with_initial_heading():
    """Rotation should add to the origin's initial heading."""
    point = GlobalPose(GlobalCoordinate(1, 0), math.pi / 4)  # 45 degrees initial
    origin = GlobalCoordinate(0, 0)
    angle = math.pi / 4  # Rotate another 45 degrees

    result = rotate_pose_around_coord(origin, point, angle)

    # Heading should be initial + rotation = 45° + 45° = 90°
    assert math.isclose(result.heading, math.pi / 2, abs_tol=1e-9)


def test_zero_rotation():
    """Rotation by 0 radians should return the same point."""
    point = GlobalPose(GlobalCoordinate(3, 4), math.pi / 6)
    origin = GlobalCoordinate(1, 1)
    angle = 0

    result = rotate_pose_around_coord(origin, point, angle)

    assert math.isclose(result.position.x, 3, abs_tol=1e-9)
    assert math.isclose(result.position.y, 4, abs_tol=1e-9)
    assert math.isclose(result.heading, math.pi / 6, abs_tol=1e-9)


def test_big_units():
    """Rotate a point 90 degrees counterclockwise around origin."""
    point = GlobalPose(GlobalCoordinate(200, 100), 0)
    origin = GlobalCoordinate(100, 100)
    angle = math.pi / 2  # 90 degrees

    result = rotate_pose_around_coord(origin, point, angle)

    print(result)
    # Point (1, 0) rotated 90° CCW around origin should be at (0, 1)
    assert math.isclose(result.position.x, 100, abs_tol=1e-9)
    assert math.isclose(result.position.y, 200, abs_tol=1e-9)
    assert math.isclose(result.heading, math.pi / 2, abs_tol=1e-9)


def test_full_rotation():
    """Rotation by 2π radians should return to original position."""
    point = GlobalPose(GlobalCoordinate(3, 4), 0)
    origin = GlobalCoordinate(0, 0)
    angle = 2 * math.pi

    result = rotate_pose_around_coord(origin, point, angle)

    assert math.isclose(result.position.x, 3, abs_tol=1e-9)
    assert math.isclose(result.position.y, 4, abs_tol=1e-9)
    # Heading wraps around
    assert math.isclose(result.heading % (2 * math.pi), 0, abs_tol=1e-9)
