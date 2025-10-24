from dataclasses import dataclass
import math


@dataclass
class Coordinate:
    """
    Global 2D coordinate with x and y values.
    """
    x: float # How much do we need to go to the right or left?
    y: float # How much do we need to go forward or backward?

    def distance_to(self, other: 'Coordinate') -> float:
        """Calculate Euclidean distance to another coordinate."""
        return math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2)

    def move(self, dx: float, dy: float) -> 'Coordinate':
        """Return a new coordinate moved by dx and dy."""
        return Coordinate(self.x + dx, self.y + dy)
