import time
from collections import deque
from statistics import median

from geometry import LocalCoordinate, PIDState
from utils.constants import MotorSide


class Motor:
    count: int
    velocity: float
    last_velocity: float
    last_confirmed_velocity_update: float = 0  # in nanoseconds
    side: MotorSide
    position: LocalCoordinate
    current_input: float = 0
    target_velocity: float = 0.0
    last_error: float = 0.0  # Track error for derivative calculation
    integral: float = 0.0  # Integral term for PID
    last_update_time: float = 0.0  # Time of last PID update

    # Last calculated PID terms (for visualization)
    last_p_term: float = 0.0
    last_d_term: float = 0.0
    last_i_term: float = 0.0

    # Median filter for velocity readings
    velocity_buffer: deque

    def __init__(self, count: int, position: LocalCoordinate, velocity: float = 0.0):
        self.count = count
        self.position = position
        self.current_input = 0.0
        self.velocity = velocity
        self.last_velocity = velocity
        self.target_velocity = 0.0
        self.last_error = 0.0
        self.integral = 0.0
        self.last_update_time = time.time()
        self.last_p_term = 0.0
        self.last_d_term = 0.0
        self.last_i_term = 0.0
        self.velocity_buffer = deque(maxlen=5)  # Keep last 5 readings for median

    def set_velocity(self, current_velocity: float):
        # Use median filter to reject outliers from encoder noise
        # Add new reading to buffer
        self.velocity_buffer.append(current_velocity)

        # Calculate median of recent readings
        if len(self.velocity_buffer) >= 3:  # Need at least 3 for meaningful median
            filtered_velocity = median(self.velocity_buffer)

            # Log if filtering removed a spike
            if abs(current_velocity - filtered_velocity) > 20.0:
                print(
                    f"Median filter: raw={current_velocity:.1f} cm/s, "
                    f"filtered={filtered_velocity:.1f} cm/s, "
                    f"buffer={[f'{v:.1f}' for v in self.velocity_buffer]}"
                )

            self.last_velocity = self.velocity
            self.velocity = filtered_velocity
        else:
            # Not enough readings yet, use raw value
            self.last_velocity = self.velocity
            self.velocity = current_velocity

        self.last_confirmed_velocity_update = time.time_ns()

    def recalculate_velocity(self):
        if self.velocity < 1e-6:
            return  # No need to recalculate if velocity is zero
        current_time = time.time_ns()
        time_delta_ns = current_time - self.last_confirmed_velocity_update
        time_delta_s = time_delta_ns / 1e9

        # Only decay if no encoder tick for a while (500ms threshold)
        decay_threshold = 0.5  # seconds
        if time_delta_s > decay_threshold:
            self.last_velocity = self.velocity
            # Gradually decay velocity toward zero (10 cm/s per second decay rate)
            decay_rate = 10.0  # cm/s per second
            time_since_threshold = time_delta_s - decay_threshold
            velocity_reduction = decay_rate * time_since_threshold

            new_velocity = max(0.0, self.velocity - velocity_reduction)
            self.velocity = new_velocity
            print(
                f"Decaying velocity: {self.velocity:.2f} cm/s "
                f"(no tick for {time_delta_s:.3f}s)"
            )

    def calculate_needed_input_based_on_velocity(self):
        self.recalculate_velocity()
        velocity_error = self.target_velocity - self.velocity

        # PID gains
        k_p = 0.02
        k_d = 0.04
        k_i = 0.001  # Integral gain

        # Calculate and store PID terms
        self.last_p_term = k_p * velocity_error

        # Derivative term (based on error change)
        derivative = velocity_error - self.last_error
        self.last_d_term = k_d * derivative

        # Integral term with anti-windup
        self.integral += velocity_error
        # Clamp integral to prevent windup (max contribution of ±20)
        max_integral = 20.0 / k_i if k_i > 0 else 0
        self.integral = max(-max_integral, min(max_integral, self.integral))
        self.last_i_term = k_i * self.integral

        motor_input_change = self.last_p_term + self.last_d_term + self.last_i_term

        motor_input = int(self.current_input + motor_input_change)
        print(
            "\t".join(
                [
                    f"velocity: {self.velocity:.3f} cm/s",
                    f"velocity error: {velocity_error:.3f} cm/s",
                    f"proportional: {self.last_p_term:.3f}",
                    f"derivative: {self.last_d_term:.3f}",
                    f"integral: {self.last_i_term:.3f}",
                    f"Calculated motor input before limits: {motor_input}",
                ]
            )
        )

        # Update error tracking
        self.last_error = velocity_error

        return motor_input

    def get_pid_state(self) -> PIDState:
        """Get current PID state for visualization."""
        return PIDState(
            timestamp=time.time(),
            target_velocity=self.target_velocity,
            actual_velocity=self.velocity,
            error=self.last_error,
            p_term=self.last_p_term,
            d_term=self.last_d_term,
            i_term=self.last_i_term,
            motor_input=self.current_input,
        )
