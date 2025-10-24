from utils import LocalCoordinate


def ultrasonic_calculation(target: LocalCoordinate) -> LocalCoordinate:
    # TODO: Based on ultrasonic data, estimate objects around something like this:
    # get_ultrasonic_hit_points(): List[LocalCoordinate]
    # Interpolate between those points to figure out where we can navigate, fx. by making a bounding box the size of the chair
    # around the translation vector we're trying to go to

    # All calculations happen in local frame (relative to robot)
    # Input: where we want to go (relative to current position)
    # Output: adjusted target that avoids obstacles (relative to current position)

    # By default, we'll go to the same target we receive, if we don't determine any problems
    return target