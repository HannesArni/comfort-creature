import math
import time
from dataclasses import dataclass

import cv2
import numpy as np
from ultralytics import YOLO

from camera.is_facing_camera import is_facing_camera
from geometry import LocalCoordinate
from utils.constants import CAMERA_COORDINATES

CAM_INDEX = 0

# Camera + person constants
CAM_HFOV_DEG = 80.0  # webcam horizontal FOV in degrees
SHOULDER_REAL_CM = 45  # average shoulder width in meters (rough)

# Use YOLOv8 pose model (boxes + keypoints)
model = YOLO("yolov8n-pose.pt")
CONF_THRESH = 0.35

# Inference resolution (smaller = faster)
INFER_W, INFER_H = 640, 360  # try 480x270 later if needed

cap = cv2.VideoCapture(CAM_INDEX)
if not cap.isOpened():
    raise SystemExit(f"Could not open camera with index {CAM_INDEX}")

# Throttle camera: lower resolution + FPS to reduce queueing/latency
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 5)  # aim for ~5 fps
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # try to keep only 1 buffered frame

print("Camera opened with YOLO pose + primary target + distance. Press 'q' to quit.")

prev_t = time.time()


@dataclass
class CameraTarget:
    coordinate: LocalCoordinate
    is_facing_camera: bool


def get_target_from_camera() -> CameraTarget or None:  # type: ignore
    if not cap.isOpened():
        print("Camera is not opened")
    t0 = time.time()
    ok, frame = cap.read()
    if not ok or frame is None:
        print("Frame grab failed")
        return
    t1 = time.time()

    H, W = frame.shape[:2]
    cx_img = W // 2
    cy_img = H // 2

    # Precompute focal length in pixels from HFOV & width
    f_px = (W / 2.0) / np.tan(np.deg2rad(CAM_HFOV_DEG) / 2.0)

    # Resize for faster YOLO
    frame_small = cv2.resize(frame, (INFER_W, INFER_H))

    # --- YOLO pose on downscaled frame ---
    results = model.predict(frame_small, imgsz=INFER_W, conf=CONF_THRESH, verbose=False)
    t2 = time.time()

    candidates = []  # each item: dict with box, conf, centroid, facing, kps

    for r in results:
        boxes = r.boxes
        kps_obj = r.keypoints  # ultralytics Keypoints object

        if boxes is None or kps_obj is None:
            continue

        xyxy_small = boxes.xyxy.cpu().numpy()  # type: ignore[union-attr]  # [N, 4] on small frame
        confs = boxes.conf.cpu().numpy()  # type: ignore[union-attr]  # [N]
        kps_small = kps_obj.xy.cpu().numpy()  # type: ignore[union-attr]  # [N, K, 2] on small frame

        for i, (box_s, p) in enumerate(zip(xyxy_small, confs)):
            x1_s, y1_s, x2_s, y2_s = box_s

            # Scale box coordinates back to full frame
            x1 = int(x1_s * W / INFER_W)
            y1 = int(y1_s * H / INFER_H)
            x2 = int(x2_s * W / INFER_W)
            y2 = int(y2_s * H / INFER_H)

            # Scale keypoints to full frame
            kps = kps_small[i].copy()
            kps[:, 0] = kps[:, 0] * W / INFER_W
            kps[:, 1] = kps[:, 1] * H / INFER_H

            # Centroid of bounding box
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            facing = is_facing_camera(kps, (x1, y1, x2, y2))

            candidates.append(
                {
                    "box": (x1, y1, x2, y2),
                    "conf": float(p),
                    "centroid": (cx, cy),
                    "facing": facing,
                    "kps": kps,
                }
            )

    # --- Choose primary target: closest to image center ---
    primary = None
    if candidates:

        def dist2_to_center(cand):
            cx, cy = cand["centroid"]
            dx = cx - cx_img
            dy = cy - cy_img
            return dx * dx + dy * dy

        primary = min(candidates, key=dist2_to_center)

    # --- Draw everything ---
    people_count = len(candidates)

    # Optional: draw boxes for all people (dim)
    for cand in candidates:
        x1, y1, x2, y2 = cand["box"]
        color = (80, 80, 80)
        thickness = 1
        if cand is primary:
            color = (0, 0, 255)
            thickness = 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    # stýra mótor eftir staðsetningu targets
    if primary is not None:
        x1, y1, x2, y2 = primary["box"]
        cx, cy = primary["centroid"]
        ...
        dx = cx - cx_img
        angle_rad = np.arctan(dx / f_px)
        angle_deg = np.degrees(angle_rad)

        print(f"angle={angle_deg:+5.1f} deg  ")

    # Draw primary target details (centroid, facing, coords, distance)
    if primary is not None:
        x1, y1, x2, y2 = primary["box"]
        cx, cy = primary["centroid"]
        conf = primary["conf"]
        facing = primary["facing"]
        kps = primary["kps"]

        # calculate angle
        dx = cx - cx_img  # pixel offset from image center
        angle_rad = np.arctan(dx / f_px)
        angle_deg = np.degrees(angle_rad)

        angle_text = f"angle {angle_deg:+.1f}°"
        cv2.putText(
            frame,
            angle_text,
            (12, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # Centroid marker
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
        cv2.drawMarker(
            frame,
            (cx, cy),
            (0, 255, 0),
            markerType=cv2.MARKER_CROSS,
            markerSize=12,
            thickness=2,
        )

        # Coordinates text
        coord_text = f"({cx},{cy})"
        cv2.putText(
            frame,
            coord_text,
            (cx + 8, cy - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )

        # Facing label
        facing_text = "facing" if facing else "not facing"
        label_color = (0, 255, 0) if facing else (0, 255, 255)
        label = f"{facing_text}  {conf:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 4), (x1 + tw + 4, y1), label_color, -1)
        cv2.putText(
            frame,
            label,
            (x1 + 2, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )

        # --- Distance estimate using shoulder width ---
        dist_cm = 0
        try:
            l_sh = kps[5]  # left shoulder (x,y)
            r_sh = kps[6]  # right shoulder (x,y)
            if not (np.allclose(l_sh, 0) or np.allclose(r_sh, 0)):
                shoulder_px = abs(l_sh[0] - r_sh[0])
                if shoulder_px > 1:
                    dist_cm = (SHOULDER_REAL_CM * f_px) / shoulder_px
        except IndexError:
            dist_cm = 0

        if dist_cm != 0:
            dist_text = f"~{dist_cm:.2f} m"
        else:
            dist_text = "~? m"
        # calculate distances
        local_y = dist_cm * math.cos(math.radians(angle_deg))
        local_x = dist_cm * math.sin(math.radians(angle_deg))

        new_dist_text = (
            dist_text
            + " x: "
            + str(round(local_y, 3))
            + " y: "
            + str(round(local_x, 3))
        )

        cv2.putText(
            frame,
            new_dist_text,
            (12, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # Optional: center marker + horizontal error for steering
        cv2.drawMarker(
            frame,
            (cx_img, cy_img),
            (255, 0, 0),
            markerType=cv2.MARKER_TILTED_CROSS,
            markerSize=14,
            thickness=1,
        )
    else:
        cv2.putText(
            frame,
            "NO TARGET (L=0, R=0)",
            (12, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )
    t3 = time.time()

    # Timing debug
    grab_ms = (t1 - t0) * 1000
    yolo_ms = (t2 - t1) * 1000
    draw_ms = (t3 - t2) * 1000
    total_ms = (t3 - t0) * 1000
    fps = 1000.0 / total_ms if total_ms > 1e-3 else 0.0

    info = f"grab {grab_ms:3.0f}ms | yolo {yolo_ms:3.0f}ms | draw {draw_ms:3.0f}ms | FPS {fps:4.1f} | People {people_count}"
    cv2.putText(
        frame,
        info,
        (12, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 0),
        2,
        cv2.LINE_AA,
    )

    # Controls whether to show debug view
    # cv2.imshow("Webcam + YOLO pose + PRIMARY target + distance", frame)
    # cv2.waitKey(1)
    # if cv2.waitKey(1) & 0xFF == ord("q"):
    #     return

    if primary is None or dist_cm == 0 or local_x is None or local_y is None:
        return None
    else:
        return CameraTarget(
            coordinate=LocalCoordinate(
                x=float(local_x) + CAMERA_COORDINATES.x,
                y=float(local_y) + CAMERA_COORDINATES.y,
            ),
            is_facing_camera=facing,
        )


def close_camera():
    cap.release()
    cv2.destroyAllWindows()
