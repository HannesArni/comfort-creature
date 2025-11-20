from geometry import LocalCoordinate
from utils.constants import MotorSide, MOTOR_INPUT_LIMIT


class Motor:
    count: int
    velocity: float
    side: MotorSide
    position: LocalCoordinate
    current_input: int = 0
    target_velocity: float = 0.0

    def __init__(self, count: int, position: LocalCoordinate, velocity: float = 0.0):
        self.count = count
        self.position = position
        self.current_input = 0
        self.velocity = velocity
        self.target_velocity = 0.0

    def calculate_needed_input_based_on_velocity(self):
        velocity_error = self.target_velocity - self.velocity

        # Simple proportional controller
        k_p = 0.1
        motor_input_change = k_p * velocity_error
        motor_input = int(self.current_input + motor_input_change)

        return motor_input
