from dataclasses import dataclass
import math


@dataclass
class GlobalCoordinate:
    """
    Global/world 2D coordinate with x and y values.
    """
    x: float  # How much to the right or left in global frame
    y: float  # How much forward or backward in global frame

    def distance_to(self, other: 'GlobalCoordinate') -> float:
        """Calculate Euclidean distance to another coordinate."""
        return math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2)

    def move(self, dx: float, dy: float) -> 'GlobalCoordinate':
        """Return a new coordinate moved by dx and dy."""
        return GlobalCoordinate(self.x + dx, self.y + dy)

    def to_local(self, pose: 'GlobalPose') -> 'LocalCoordinate':
        """Convert to local coordinates relative to a given pose."""
        # Translate to pose origin
        dx = self.x - pose.x
        dy = self.y - pose.y

        # Rotate by -heading to get local coordinates
        cos_h = math.cos(-pose.heading)
        sin_h = math.sin(-pose.heading)

        local_x = dx * cos_h - dy * sin_h
        local_y = dx * sin_h + dy * cos_h

        return LocalCoordinate(local_x, local_y)


@dataclass
class LocalCoordinate:
    """
    Local coordinate relative to robot/chair position.
    x: right/left relative to robot
    y: forward/backward relative to robot
    """
    x: float
    y: float

    def distance_to(self, other: 'LocalCoordinate') -> float:
        """Calculate Euclidean distance to another coordinate."""
        return math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2)

    def to_global(self, pose: 'GlobalPose') -> GlobalCoordinate:
        """Convert to global coordinates given the current pose."""
        # Rotate by heading
        cos_h = math.cos(pose.heading)
        sin_h = math.sin(pose.heading)

        global_x = self.x * cos_h - self.y * sin_h + pose.x
        global_y = self.x * sin_h + self.y * cos_h + pose.y

        return GlobalCoordinate(global_x, global_y)


@dataclass
class GlobalPose:
    """
    Robot/chair position and orientation in global coordinates.
    """
    x: float
    y: float
    heading: float  # radians, 0 = facing along positive y-axis

    def move(self, dx: float, dy: float, dheading: float = 0.0) -> 'GlobalPose':
        """Return a new pose moved by dx, dy, and rotated by dheading."""
        return GlobalPose(self.x + dx, self.y + dy, self.heading + dheading)
