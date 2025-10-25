import math

from geometry import LocalCoordinate, LocalPose, UltrasonicSensor

sensors = [
    UltrasonicSensor(
        pose=LocalPose(position=LocalCoordinate(30, 30), heading=math.radians(45)),
        name="Front-Left",
    ),
    UltrasonicSensor(
        pose=LocalPose(position=LocalCoordinate(0, 30), heading=0), name="Front"
    ),
    UltrasonicSensor(
        pose=LocalPose(
            position=LocalCoordinate(-30, 30), heading=math.radians(365 - 45)
        ),
        name="Front-Right",
    ),
]


def get_ultrasonic_hit_points() -> list[LocalCoordinate]:
    hit_points: list[LocalCoordinate] = []
    for sensor in sensors:
        # TODO: Replace with actual reading from sensor,
        # let's work with 100 cm for now
        distance_reading = 100

        # You remember pythagoras from school, right?
        x_translation = distance_reading * math.sin(sensor.pose.heading)
        y_translation = distance_reading * math.cos(sensor.pose.heading)

        hit_point = sensor.pose.position.move(x_translation, y_translation)
        hit_points.append(hit_point)

    return hit_points
