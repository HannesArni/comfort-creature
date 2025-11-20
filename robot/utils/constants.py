import math
from enum import Enum

from geometry import LocalCoordinate


class MotorSide(Enum):
    RIGHT = 1
    LEFT = 2


MOTOR_DIAMETER = 25  # cm
MOTOR_PERIMITER = MOTOR_DIAMETER * math.pi  # cm
ENCODER_TICKS_PER_REVOLUTION = 60  # ticks
CM_PER_TICK = MOTOR_PERIMITER / ENCODER_TICKS_PER_REVOLUTION  # cm/tick

LEFT_MOTOR_COORDINATES = LocalCoordinate(-20, 13)
RIGHT_MOTOR_COORDINATES = LocalCoordinate(20, 13)
