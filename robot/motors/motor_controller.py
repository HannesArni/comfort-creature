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
from utils.constants import (
    CM_PER_TICK,
    LEFT_MOTOR_COORDINATES,
    RIGHT_MOTOR_COORDINATES,
    MotorSide,
)


@dataclass
class Motor:
    count: int
    velocity: float
    position: LocalCoordinate


@dataclass
class Motors:
    left: Motor
    right: Motor

    def __getitem__(self, side: MotorSide) -> Motor:
        if side == MotorSide.LEFT:
            return self.left
        elif side == MotorSide.RIGHT:
            return self.right
        raise KeyError(f"Invalid motor side: {side}")

    def __setitem__(self, side: MotorSide, motor: Motor) -> None:
        if side == MotorSide.LEFT:
            self.left = motor
        elif side == MotorSide.RIGHT:
            self.right = motor
        else:
            raise KeyError(f"Invalid motor side: {side}")


class MotorController:
    """Controls differential drive motors via serial communication with Arduino."""

    def __init__(self):
        self.motors: Motors = Motors(
            left=Motor(count=0, position=LEFT_MOTOR_COORDINATES, velocity=0.0),
            right=Motor(count=0, position=RIGHT_MOTOR_COORDINATES, velocity=0.0),
        )
        self.pose: GlobalPose = GlobalPose(GlobalCoordinate(1090.0, 30.0), 0.0)
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
            self.motors[reading.motor].velocity = CM_PER_TICK / (
                reading.dt / 1000
            )  # cm/s
            print(reading.motor, self.motors[reading.motor].velocity, "cm/s")

            self.pose = transform_on_encoder(
                reading,
                self.pose,
                self.motors.left.position,
                self.motors.right.position,
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
