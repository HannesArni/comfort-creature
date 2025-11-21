def is_facing_camera(kps, box, horiz_tol=0.18):
    """
    Heuristic: use nose + shoulders.

    kps: (K, 2) full-res keypoints (x,y)
    box: (x1, y1, x2, y2) full-res box
    horiz_tol: tolerance as fraction of box width
    """
    x1, y1, x2, y2 = box
    box_w = max(x2 - x1, 1)

    # COCO-style keypoint indices for YOLOv8 pose:
    # 0 nose, 5 left shoulder, 6 right shoulder
    try:
        nose = kps[0]
        l_sh = kps[5]
        r_sh = kps[6]
    except IndexError:
        return False

    # If any are (0,0), assume missing
    if np.allclose(nose, 0) or np.allclose(l_sh, 0) or np.allclose(r_sh, 0):
        return False

    nose_x = nose[0]
    l_sh_x = l_sh[0]
    r_sh_x = r_sh[0]

    shoulder_mid_x = 0.5 * (l_sh_x + r_sh_x)
    # how far nose is from the midpoint of shoulders, normalized by box width
    offset = abs(nose_x - shoulder_mid_x) / box_w

    return offset < horiz_tol
