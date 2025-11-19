import math

from geometry import GlobalCoordinate, GlobalPose


def rotate_pose_around_coord(origin: GlobalPose, point: GlobalCoordinate, angle: float):
    """
    Rotate a pose counterclockwise by a given angle around a given origin.

    The angle should be given in radians.

    https://www.youtube.com/watch?v=Nen34L1qVIk
    """
    ox, oy, oh = origin.position.x, origin.position.y, origin.heading
    px, py = point.x, point.y

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return GlobalPose(GlobalCoordinate(qx, qy), oh + angle)
