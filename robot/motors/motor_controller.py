"""
Motor controller for Arduino-based differential drive system.

Communicates with Arduino via serial to control left and right motors.
Uses the command protocol defined in motor-interface CLI.
"""

import time
from dataclasses import dataclass

from geometry import GlobalCoordinate, GlobalPose
from motors.motor import Motor
from motors.parse_encoder_line import parse_encoder_line
from motors.serial_protocol import SerialProtocol
from motors.transform_on_encoder import transform_on_encoder
from utils import config
from utils.constants import (
    CM_PER_TICK,
    LEFT_MOTOR_COORDINATES,
    MAX_MOTOR_INPUT_RANGE,
    MIN_MOTOR_INPUT_RANGE,
    MOTOR_INPUT_LIMIT,
    RIGHT_MOTOR_COORDINATES,
    MotorSide,
)
from utils.map_range import map_range


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
        self.pose: GlobalPose = GlobalPose(GlobalCoordinate(0.0, 0.0), 0.0)
        self._last_command_time = time.time()
        self.protocol = SerialProtocol(on_line=self._handle_serial_line)
        self.in_automatic_mode = False

    async def connect(self) -> bool:
        return await self.protocol.connect(
            config.arduino_port, config.arduino_baud_rate
        )

    def disconnect(self):
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
            motor = self.motors[reading.motor]
            if reading.dt:
                motor.set_velocity(CM_PER_TICK / (reading.dt / 1000))

            self.pose = transform_on_encoder(
                reading,
                self.pose,
                self.motors.left.position,
                self.motors.right.position,
            )
        else:
            # Other messages (status, errors, etc.)
            print(f"Arduino: {line}")

    async def set_motor(self, side: MotorSide, input_speed: float):
        """input speed range: (0-100)."""
        constrained_speed = max(0.0, min(100.0, input_speed))
        self.motors[side].current_input = constrained_speed

        mapped_speed = round(
            map_range(
                constrained_speed, 0, 100, MIN_MOTOR_INPUT_RANGE, MAX_MOTOR_INPUT_RANGE
            )
        )
        capped_speed = min(mapped_speed, MOTOR_INPUT_LIMIT) if input_speed > 0 else 0
        await self._send_command(f"{side.value.lower()} {capped_speed}")

    async def target_velocity_test(self):
        if not self.in_automatic_mode:
            return
        left_motor = self.motors[MotorSide.LEFT]
        left_motor.target_velocity = 40
        needed_input = left_motor.calculate_needed_input_based_on_velocity()
        await self.set_motor(MotorSide.LEFT, needed_input)

        right_motor = self.motors[MotorSide.RIGHT]
        right_motor.target_velocity = 40
        needed_input = right_motor.calculate_needed_input_based_on_velocity()
        await self.set_motor(MotorSide.RIGHT, needed_input)

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
