import numpy as np

# horiz_tol: tolerance as fraction of box width
FACING_THRESHOLD = 0.18


def is_facing_camera(kps, bounding_box):
    """
    Heuristic: use nose + shoulders.

    kps: (K, 2) full-res keypoints (x,y)
    bounding_box: (x1, y1, x2, y2) full-res bounding_box
    horiz_tol: tolerance as fraction of bounding_box width
    """
    x1, y1, x2, y2 = bounding_box
    box_w = max(x2 - x1, 1)

    # COCO-style keypoint indices for YOLOv8 pose:
    # 0 nose, 5 left shoulder, 6 right shoulder
    try:
        nose = kps[0]
        left_shoulder = kps[5]
        right_shoulder = kps[6]
    except IndexError:
        return False

    # If any are (0,0), assume missing
    if (
        np.allclose(nose, 0)
        or np.allclose(left_shoulder, 0)
        or np.allclose(right_shoulder, 0)
    ):
        return False
    nose_x = nose[0]
    left_shoulder_x = left_shoulder[0]
    right_shoulder_x = right_shoulder[0]

    if left_shoulder_x < right_shoulder_x:
        return False

    shoulder_mid_x = 0.5 * (left_shoulder_x + right_shoulder_x)
    # how far nose is from the midpoint of shoulders, normalized by box width
    offset = abs(nose_x - shoulder_mid_x) / box_w

    return True
