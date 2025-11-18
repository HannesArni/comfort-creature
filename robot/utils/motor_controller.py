"""
Motor controller for Arduino-based differential drive system.

Communicates with Arduino via serial to control left and right motors.
Uses the command protocol defined in motor-interface CLI.
"""

import time
from typing import Optional

import serial


class MotorController:
    """Controls differential drive motors via serial communication with Arduino."""

    def __init__(self, port: Optional[str] = None, baud_rate: int = 9600):
        """
        Initialize motor controller.

        Args:
            port: Serial port path (e.g., '/dev/ttyUSB0'). If None, attempts auto-detection.
            baud_rate: Serial communication speed (default: 9600)
        """
        self.ser: Optional[serial.Serial] = None
        self.port = port
        self.baud_rate = baud_rate
        self._last_command_time = time.time()

    def connect(self) -> bool:
        """
        Connect to Arduino.

        Returns:
            True if connection successful, False otherwise
        """
        if self.port is None:
            self.port = self._find_arduino_port()

        if self.port is None:
            print("Could not find Arduino port")
            return False

        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            print(f"Connected to Arduino on {self.port}")
            return True
        except Exception as e:
            print(f"Error connecting to Arduino: {e}")
            return False

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

    def set_left_motor(self, speed: int):
        """
        Set left motor speed.

        Args:
            speed: Motor speed (-255 to 255)
        """
        speed = max(-255, min(255, speed))  # Clamp to valid range
        self._send_command(f"left {speed}")

    def set_right_motor(self, speed: int):
        """
        Set right motor speed.

        Args:
            speed: Motor speed (-255 to 255)
        """
        speed = max(-255, min(255, speed))  # Clamp to valid range
        self._send_command(f"right {speed}")

    def set_both_motors(self, left_speed: int, right_speed: int):
        """
        Set both motor speeds.

        Args:
            left_speed: Left motor speed (-255 to 255)
            right_speed: Right motor speed (-255 to 255)
        """
        left_speed = max(-255, min(255, left_speed))
        right_speed = max(-255, min(255, right_speed))
        self._send_command(f"left {left_speed}")
        self._send_command(f"right {right_speed}")

    def stop(self):
        """Stop both motors."""
        self._send_command("stop")

    def get_status(self):
        """Request motor status from Arduino."""
        self._send_command("status")

    def keep_alive(self):
        """
        Send keep-alive command to prevent Arduino timeout.

        Should be called at least once per second to maintain current motor speeds.
        """
        # Send a harmless status command to reset Arduino's timeout timer
        if time.time() - self._last_command_time > 0.5:
            self._send_command("status")

    @staticmethod
    def _find_arduino_port() -> Optional[str]:
        """
        Attempt to auto-detect Arduino port.

        Returns:
            Port path if found, None otherwise
        """
        common_ports = [
            "/dev/cu.usbmodem14101",
            "/dev/cu.usbmodem141101",
            "/dev/ttyUSB0",
            "/dev/ttyUSB1",
            "/dev/ttyACM0",
            "/dev/cu.usbserial",
        ]

        for port in common_ports:
            try:
                ser = serial.Serial(port, 9600, timeout=1)
                ser.close()
                return port
            except (OSError, serial.SerialException):
                continue

        return None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
