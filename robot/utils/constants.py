import math
from enum import Enum

from geometry import LocalCoordinate


class MotorSide(Enum):
    RIGHT = "right"
    LEFT = "left"


MOTOR_DIAMETER = 25  # cm
MOTOR_PERIMITER = MOTOR_DIAMETER * math.pi  # cm
ENCODER_TICKS_PER_REVOLUTION = 60  # ticks
CM_PER_TICK = MOTOR_PERIMITER / ENCODER_TICKS_PER_REVOLUTION  # cm/tick

LEFT_MOTOR_COORDINATES = LocalCoordinate(-20, 13)
RIGHT_MOTOR_COORDINATES = LocalCoordinate(20, 13)
CAMERA_COORDINATES = LocalCoordinate(0, 10)

CHAIR_WIDTH = 73
CHAIR_LENGTH = 67

# Range is 0-255, but some inputs are not used
MIN_MOTOR_INPUT_RANGE = 60
MOTOR_INPUT_LIMIT = 120
MAX_MOTOR_INPUT_RANGE = 150

DISTANCE_OCCUPIED_UPPER_THRESHOLD_CM = 11.5
