"""
Motor controller for Arduino-based differential drive system.

Communicates with Arduino via serial to control left and right motors.
Uses the command protocol defined in motor-interface CLI.
"""

import time
from dataclasses import dataclass

from geometry import GlobalCoordinate, GlobalPose, LocalCoordinate
from motors.parse_encoder_line import parse_encoder_line
from motors.serial_protocol import SerialProtocol
from motors.transform_on_encoder import transform_on_encoder
from utils import config


@dataclass
class Motor:
    count: int
    position: LocalCoordinate


class MotorController:
    """Controls differential drive motors via serial communication with Arduino."""

    def __init__(self):
        self.left: Motor = Motor(count=0, position=LocalCoordinate(-20, 13))
        self.right: Motor = Motor(count=0, position=LocalCoordinate(20, 13))
        self.pose: GlobalPose = GlobalPose(GlobalCoordinate(0.0, 0.0), 0.0)
        self._last_command_time = time.time()
        self.protocol = SerialProtocol(on_line=self._handle_serial_line)

    async def connect(self) -> bool:
        """
        Establish async serial connection to Arduino.

        Returns:
            True if connection successful, False otherwise
        """
        return await self.protocol.connect(
            config.arduino_port, config.arduino_baud_rate
        )

    def disconnect(self):
        """Close serial connection."""
        if self.protocol.is_connected():
            self.stop_sync()  # Safety: stop motors before disconnecting
            self.protocol.close()
            print("Disconnected from Arduino")

    def is_connected(self) -> bool:
        """Check if connected to Arduino."""
        return self.protocol.is_connected()

    async def _send_command(self, command: str):
        """
        Send command to Arduino asynchronously.

        Args:
            command: Command string (e.g., "left 255", "stop")
        """
        self.protocol.send_command(command)
        self._last_command_time = time.time()

    def _send_command_sync(self, command: str):
        """Synchronous version for use in disconnect/cleanup."""
        self.protocol.send_command(command)

    def _handle_serial_line(self, line: str):
        """Handle a line received from serial (callback from protocol)."""
        # Try to parse as encoder reading
        reading = parse_encoder_line(line)
        if reading:
            self.pose = transform_on_encoder(
                reading, self.pose, self.left.position, self.right.position
            )
        else:
            # Other messages (status, errors, etc.)
            print(f"Arduino: {line}")

    async def set_left_motor(self, speed: int):
        """Set left motor speed (0-255)."""
        speed = max(0, min(255, speed))
        await self._send_command(f"left {speed}")

    async def set_right_motor(self, speed: int):
        """Set right motor speed (0-255)."""
        speed = max(0, min(255, speed))
        await self._send_command(f"right {speed}")

    async def set_both_motors(self, left_speed: int, right_speed: int):
        """Set both motor speeds (0-255)."""
        left_speed = max(0, min(255, left_speed))
        right_speed = max(0, min(255, right_speed))
        await self._send_command(f"left {left_speed}")
        await self._send_command(f"right {right_speed}")

    async def stop(self):
        """Stop both motors (async)."""
        await self._send_command("stop")

    def stop_sync(self):
        """Stop both motors (sync, for use in disconnect/cleanup)."""
        self._send_command_sync("stop")

    async def get_status(self):
        """Request status from Arduino."""
        await self._send_command("status")

    async def keep_alive(self):
        """
        Send keep-alive command to prevent Arduino timeout.

        Should be called at least once per second to maintain current motor speeds.
        """
        if time.time() - self._last_command_time > 0.5:
            await self._send_command("status")
