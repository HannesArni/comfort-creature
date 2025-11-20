import math

from geometry import GlobalCoordinate, GlobalPose


def rotate_pose_around_coord(origin: GlobalCoordinate, pose: GlobalPose, angle: float):
    """
    Rotate a pose counterclockwise by a given angle around a given origin.

    The angle should be given in radians.

    https://www.youtube.com/watch?v=Nen34L1qVIk
    """
    ox, oy = origin.x, origin.y
    px, py, ph = pose.position.x, pose.position.y, pose.heading

    new_x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    new_y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return GlobalPose(GlobalCoordinate(new_x, new_y), ph + angle)
