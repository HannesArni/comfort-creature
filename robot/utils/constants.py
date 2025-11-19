import math
from enum import Enum


class MotorSide(Enum):
    RIGHT = 1
    LEFT = 2


MOTOR_DIAMETER = 27  # cm
MOTOR_PERIMITER = MOTOR_DIAMETER * math.pi  # cm
ENCODER_TICKS_PER_REVOLUTION = 120  # ticks
CM_PER_TICK = MOTOR_PERIMITER / ENCODER_TICKS_PER_REVOLUTION  # cm/tick
