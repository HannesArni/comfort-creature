from utils import Coordinate


def ultrasonic_calculation(target: Coordinate):
    # TODO: Based on ultrasonic data, estimate objects around something like this:
    # get_ultrasonic_hit_points(): List[Coordinate]
    # Interpolate between those points to figure out where we can navigate, fx. by making a bounding box the size of the chair
    # around the translation vector we're trying to go to

    # By default, we'll go to the same target we receive, if we don't determine any problems
    return target