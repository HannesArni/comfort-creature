from geometry import LocalCoordinate
from utils.get_ultrasonic_hit_points import get_ultrasonic_hit_points


def ultrasonic_calculation(target: LocalCoordinate) -> LocalCoordinate:
    # TODO: Based on ultrasonic data, estimate objects around something
    # like this:
    _hit_points = get_ultrasonic_hit_points()  # noqa: F841
    # Interpolate between those points to figure out where we can
    # navigate, fx. by making a bounding box the size of the chair
    # around the translation vector we're trying to go to

    # All calculations happen in local frame (relative to robot)
    # Input: where we want to go (relative to current position)
    # Output: adjusted target that avoids obstacles (relative to
    # current position)

    # By default, we'll go to the same target we receive, if we
    # don't determine any problems
    return target
