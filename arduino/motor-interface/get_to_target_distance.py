#!/usr/bin/env python3
"""
Reads and parses motor encoder data from Arduino with PID control.
Expected format: LEFT: is_forward:1 count:2 dt:21
"""

import sys
import time
from dataclasses import dataclass

import serial


@dataclass
class EncoderReading:
    """Represents a single encoder reading from one motor."""

    motor: str  # "LEFT" or "RIGHT"
    is_forward: bool
    count: int
    dt: int  # Time delta in milliseconds


class PIDController:
    """Simple PID controller for motor speed control."""

    def __init__(self, kp: float, ki: float, kd: float):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0.0
        self.integral = 0.0

    def update(self, error: float, dt: float) -> float:
        """Calculate PID output given error and time delta."""
        if dt == 0:
            return 0.0

        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        return output

    def reset(self):
        """Reset PID state."""
        self.prev_error = 0.0
        self.integral = 0.0


def find_arduino_port():
    """Try common Arduino port names."""
    common_ports = [
        "/dev/cu.usbmodem14101",
        "/dev/cu.usbmodem141101",
        "/dev/ttyUSB1",
        "/dev/ttyACM0",
        "/dev/cu.usbserial",
    ]
    for port in common_ports:
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            print(f"Connected to Arduino on {port}")
            return ser
        except (OSError, serial.SerialException):
            continue
    return None


def parse_encoder_line(line: str) -> EncoderReading | None:
    """
    Parse a line like 'LEFT: is_forward:1 count:2 dt:21'
    Returns EncoderReading or None if parsing fails.
    """
    try:
        # Split motor name from data
        parts = line.split(":", 1)
        if len(parts) != 2:
            return None

        motor = parts[0].strip()
        data_str = parts[1].strip()

        # Parse key:value pairs
        data = {}
        for pair in data_str.split():
            key, value = pair.split(":")
            data[key] = value

        # Extract values
        return EncoderReading(
            motor=motor,
            is_forward=bool(int(data["is_forward"])),
            count=int(data["count"]),
            dt=int(data["dt"]),
        )
    except (ValueError, KeyError, IndexError):
        return None


def main():
    # Connect to Arduino
    ser = find_arduino_port()
    if ser is None:
        print("Could not find Arduino. Please specify port manually.")
        print("Usage: python read_motor_encoders.py [port]")
        if len(sys.argv) > 1:
            port = sys.argv[1]
            try:
                ser = serial.Serial(port, 115200, timeout=1)
                print(f"Connected to Arduino on {port}")
            except Exception as e:
                print(f"Error connecting to {port}: {e}")
                return
        else:
            return

    # Wait for Arduino to reset
    time.sleep(2)

    # PID controllers for each motor
    pid_left = PIDController(kp=0.1, ki=0.1, kd=2)
    pid_right = PIDController(kp=0.05, ki=0.1, kd=2)

    # Motor state tracking
    current_counts = {"LEFT": 0, "RIGHT": 0}
    target_count = 800  # Target count for both motors
    motor_speeds = {"LEFT": 50, "RIGHT": 50}  # Current motor speeds (50-100)

    # Control loop timing
    control_rate = 20  # Hz
    control_period = 1.0 / control_rate
    last_control_time = time.time()

    print("PID Motor Control - Targeting count:", target_count)
    print(f"Control loop rate: {control_rate} Hz")
    print("Reading motor encoder data (Ctrl+C to exit)...")
    print("-" * 60)

    try:
        while True:
            current_time = time.time()

            # Read any available serial data (non-blocking)
            while ser.in_waiting > 0:
                line = ser.readline().decode("utf-8").rstrip()
                reading = parse_encoder_line(line)
                if reading:
                    current_counts[reading.motor] = reading.count
            #                 else:
            #                     print(f"Raw: {line}")

            # Run control loop at fixed rate
            if current_time - last_control_time >= control_period:
                dt_seconds = current_time - last_control_time
                last_control_time = current_time

                # Synchronize motors - adjust speeds to keep them at the same count
                left_count = current_counts["LEFT"]
                right_count = current_counts["RIGHT"]
                count_diff = left_count - right_count  # Positive means LEFT is ahead

                # Sync correction factor (how much to slow down the leading motor)
                sync_correction = 10  # Speed reduction per count difference

                # Update both motors
                for motor in ["LEFT", "RIGHT"]:
                    error_to_target = target_count - current_counts[motor]

                    if error_to_target <= 0:
                        # At or past target, stop
                        new_speed = 0
                        motor_speeds[motor] = 0
                    else:
                        # Calculate base speed from PID controller
                        if motor == "LEFT":
                            pid_output = pid_left.update(error_to_target, dt_seconds)
                            # If LEFT is ahead, reduce its speed
                            sync_adjustment = (
                                -abs(count_diff) * sync_correction
                                if count_diff > 0
                                else 0
                            )
                        else:  # RIGHT
                            pid_output = pid_right.update(error_to_target, dt_seconds)
                            # If RIGHT is ahead, reduce its speed
                            sync_adjustment = (
                                -abs(count_diff) * sync_correction
                                if count_diff < 0
                                else 0
                            )

                        # Apply PID output and sync adjustment
                        new_speed = motor_speeds[motor] + pid_output + sync_adjustment
                        new_speed = max(50, min(80, int(new_speed)))
                        motor_speeds[motor] = new_speed

                    # Send speed command to Arduino
                    command = f"{motor} {new_speed}\n"
                    ser.write(command.encode())

                # Display status
                print(
                    f"LEFT: {current_counts['LEFT']:>4}/{target_count} "
                    f"Speed: {motor_speeds['LEFT']:>3} | "
                    f"RIGHT: {current_counts['RIGHT']:>4}/{target_count} "
                    f"Speed: {motor_speeds['RIGHT']:>3}"
                )

            # Small sleep to prevent busy waiting
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\nStopping motors...")
        ser.write(b"LEFT 0\n")
        ser.write(b"RIGHT 0\n")
        time.sleep(0.1)
        print("Closing connection...")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
