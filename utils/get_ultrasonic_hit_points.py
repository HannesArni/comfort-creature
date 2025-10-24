import math
from dataclasses import dataclass
from utils import LocalPose, LocalCoordinate


@dataclass
class UltrasonicSensor:
    """
    Where is the sensor located on the chair?
    """
    pose: LocalPose
    name: str = "Ultrasonic Sensor"

sensors = [
    UltrasonicSensor(LocalPose(LocalCoordinate(30, 30), math.radians(45)), 'Front-Left'),
    UltrasonicSensor(LocalPose(LocalCoordinate(30, 30), 0), 'Front'),
    UltrasonicSensor(LocalPose(LocalCoordinate(-30, 30), math.radians(365-45)), 'Front-Right'),
]

def get_ultrasonic_hit_points() -> list[LocalCoordinate]:
    hit_points: list[LocalCoordinate] = []
    for sensor in sensors:
        distance_reading = 100  # TODO: Replace with actual reading from sensor, let's work with 100 cm for now

        # You remember pythagoras from school, right?
        x_translation = distance_reading * math.sin(sensor.pose.heading)
        y_translation = distance_reading * math.cos(sensor.pose.heading)

        hit_point = sensor.pose.position.move(x_translation, y_translation)
        hit_points.append(hit_point)
        print(f"Sensor {sensor.name} at position {sensor.pose.position} with heading {sensor.pose.heading} reads distance {distance_reading} cm, hit point at {hit_point}")

    return hit_points


