# Coordinate System

This module defines the coordinate system used for navigation and obstacle avoidance.

## Axis Convention

- **x-axis**: Right (positive) / Left (negative)
- **y-axis**: Forward (positive) / Backward (negative)
- **Origin**: (0, 0) represents the starting position in global coordinates, or the robot's current position in local coordinates

## Heading Convention

Heading is measured in **radians** using the mathematical convention:

- **0 radians**: Facing forward along the positive y-axis (north)
- **π/2 radians (90°)**: Facing left along the negative x-axis (west)
- **π radians (180°)**: Facing backward along the negative y-axis (south)
- **3π/2 radians (270°)**: Facing right along the positive x-axis (east)

**Rotation direction**: Counter-clockwise is positive (following the mathematical right-hand rule)
- Turning left (counter-clockwise) = increasing heading
- Turning right (clockwise) = decreasing heading

## Coordinate Frames

The system uses two coordinate frames:

### Global Coordinates
- Fixed world frame
- Absolute positions that don't change as the robot moves
- Used for: waypoints, obstacle maps, target destinations

### Local Coordinates
- Relative to the robot's current position and orientation
- The robot is always at (0, 0) facing along the positive y-axis in its local frame
- Used for: sensor readings, immediate obstacle avoidance, motion planning

## Type System

- `GlobalCoordinate`: A position (x, y) in the global frame
- `LocalCoordinate`: A position (x, y) in the robot's local frame
- `GlobalPose`: A position and heading in the global frame
- `LocalPose`: A position and heading relative to the robot

All types support conversion between global and local frames using the `to_global()` and `to_local()` methods.

## Example

```python
from coordinates import GlobalCoordinate, GlobalPose, LocalCoordinate

# Robot is at global position (10, 5) facing 90° to the left (π/2 radians)
current_pose = GlobalPose(
    position=GlobalCoordinate(10.0, 5.0),
    heading=1.5708  # π/2 radians
)

# Obstacle detected at global position (15, 10)
obstacle = GlobalCoordinate(15.0, 10.0)

# Convert to local frame to understand where obstacle is relative to robot
local_obstacle = obstacle.to_local(current_pose)
# local_obstacle.x tells us how far right (+) or left (-) the obstacle is
# local_obstacle.y tells us how far ahead (+) or behind (-) the obstacle is
```
