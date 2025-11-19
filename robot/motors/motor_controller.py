"""
Motor controller for Arduino-based differential drive system.

Communicates with Arduino via serial to control left and right motors.
Uses the command protocol defined in motor-interface CLI.
"""

import time
from dataclasses import dataclass
from typing import Optional

import serial

from geometry import GlobalCoordinate, GlobalPose, LocalCoordinate
from motors.parse_encoder_line import parse_encoder_line
from motors.transform_on_encoder import transform_on_encoder
from utils import config


@dataclass
class Motor:
    count: int
    position: LocalCoordinate = LocalCoordinate(0.0, 0.0)


class MotorController:
    """Controls differential drive motors via serial communication with Arduino."""

    ser: Optional[serial.Serial]
    left: Motor = Motor(count=0, position=LocalCoordinate(-30, 30))
    right: Motor = Motor(count=0, position=LocalCoordinate(30, 30))
    pose: GlobalPose = GlobalPose(GlobalCoordinate(0.0, 0.0), 0.0)

    def __init__(self):
        self._last_command_time = time.time()

    def connect(self):
        self.ser = serial.Serial(
            config.arduino_port, config.arduino_baud_rate, timeout=1
        )
        time.sleep(2)  # Wait for Arduino to reset
        print(f"Connected to Arduino on {self.port}")

    def disconnect(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.stop()  # Safety: stop motors before disconnecting
            self.ser.close()
            print("Disconnected from Arduino")

    def _send_command(self, command: str):
        """
        Send command to Arduino.

        Args:
            command: Command string (e.g., "left 255", "stop")
        """
        if not self.ser or not self.ser.is_open:
            print("Error: Not connected to Arduino")
            return

        try:
            self.ser.write(f"{command}\n".encode())
            self._last_command_time = time.time()
            # Read response (if any)
            time.sleep(0.01)  # Small delay for Arduino to respond
            while self.ser.in_waiting > 0:
                response = self.ser.readline().decode("utf-8").rstrip()
                print(f"Arduino: {response}")
        except Exception as e:
            print(f"Error sending command '{command}': {e}")

    def parse_serial(self):
        if not self.ser or not self.ser.is_open:
            print("Error: Not connected to Arduino")
            return

        while self.ser.in_waiting > 0:
            line = self.ser.readline().decode("utf-8").rstrip()
            reading = parse_encoder_line(line)
            if not reading:
                continue

            self.pose = transform_on_encoder(
                reading, self.pose, reading, self.left, self.right
            )

    def set_left_motor(self, speed: int):
        speed = max(0, min(255, speed))  # Clamp to valid range
        self._send_command(f"left {speed}")

    def set_right_motor(self, speed: int):
        speed = max(0, min(255, speed))  # Clamp to valid range
        self._send_command(f"right {speed}")

    def set_both_motors(self, left_speed: int, right_speed: int):
        left_speed = max(0, min(255, left_speed))
        right_speed = max(0, min(255, right_speed))
        self._send_command(f"left {left_speed}")
        self._send_command(f"right {right_speed}")

    def stop(self):
        self._send_command("stop")

    def get_status(self):
        self._send_command("status")

    def keep_alive(self):
        """
        Send keep-alive command to prevent Arduino timeout.

        Should be called at least once per second to maintain current motor speeds.
        """
        # Send a harmless status command to reset Arduino's timeout timer
        if time.time() - self._last_command_time > 0.5:
            self._send_command("status")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
