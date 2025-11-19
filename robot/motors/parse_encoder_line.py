from dataclasses import dataclass

from utils.constants import MotorSide


@dataclass
class EncoderReading:
    """Represents a single encoder reading from one motor."""

    motor: MotorSide  # "LEFT" or "RIGHT"
    is_forward: bool
    count: int
    dt: int  # Time delta in milliseconds


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

        raw_motor = parts[0].strip()
        motor = MotorSide.LEFT if raw_motor.upper() == "LEFT" else MotorSide.RIGHT
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
