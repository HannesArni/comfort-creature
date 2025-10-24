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
        dx = self.x - pose.position.x
        dy = self.y - pose.position.y

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

    def move(self, dx: float, dy: float) -> 'LocalCoordinate':
        """Return a new coordinate moved by dx and dy."""
        return LocalCoordinate(self.x + dx, self.y + dy)

    def to_global(self, pose: 'GlobalPose') -> GlobalCoordinate:
        """Convert to global coordinates given the current pose."""
        # Rotate by heading
        cos_h = math.cos(pose.heading)
        sin_h = math.sin(pose.heading)

        global_x = self.x * cos_h - self.y * sin_h + pose.position.x
        global_y = self.x * sin_h + self.y * cos_h + pose.position.y

        return GlobalCoordinate(global_x, global_y)


@dataclass
class LocalPose:
    """
    Position and orientation in local coordinates (relative to robot).
    """
    position: LocalCoordinate
    heading: float  # radians, relative to robot's current heading. Positive is counter-clockwise.

    def to_global(self, current_pose: 'GlobalPose') -> 'GlobalPose':
        """Convert to global pose given the current robot pose."""
        # Convert local coordinate to global
        global_position = self.position.to_global(current_pose)
        global_heading = current_pose.heading + self.heading

        return GlobalPose(global_position, global_heading)


@dataclass
class GlobalPose:
    """
    Robot/chair position and orientation in global coordinates.
    """
    position: GlobalCoordinate
    heading: float  # radians, 0 = facing along positive y-axis. Positive is counter-clockwise.

    def move(self, dx: float, dy: float, dheading: float = 0.0) -> 'GlobalPose':
        """Return a new pose moved by dx, dy, and rotated by dheading."""
        new_position = self.position.move(dx, dy)
        return GlobalPose(new_position, self.heading + dheading)

    def to_local(self, reference_pose: 'GlobalPose') -> LocalPose:
        """Convert to local pose relative to a reference pose."""
        # Convert position to local coordinates
        local_position = self.position.to_local(reference_pose)
        local_heading = self.heading - reference_pose.heading

        return LocalPose(local_position, local_heading)
