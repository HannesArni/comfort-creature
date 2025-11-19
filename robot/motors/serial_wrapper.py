import time
from typing import Optional

import serial


class SerialWrapper:
    def __init__(self, port: str, baud_rate: int):
        """
        Initialize motor controller.

        Args:
            port: Serial port path (e.g., '/dev/ttyUSB0')
            baud_rate: Serial communication speed (default: 115200)
        """
        self.ser: Optional[serial.Serial] = None
        self.port = port
        self.baud_rate = baud_rate

    def connect(self):
        """
        Connect to Arduino.

        Returns:
            True if connection successful, False otherwise
        """

        self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        print(f"Connected to Arduino on {self.port}")

    def disconnect(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.stop()  # Safety: stop motors before disconnecting
            self.ser.close()
            print("Disconnected from Arduino")
