from utils import Coordinate
from utils.ultrasonic_calculation import ultrasonic_calculation


def main():
    print("Hello, World!")
    target = Coordinate(10, 4)
    ultrasonic_calculation(target)


if __name__ == "__main__":
    main()
