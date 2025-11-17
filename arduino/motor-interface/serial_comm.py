#!/usr/bin/env python3
"""
Simple serial communication script for Arduino.
Reads digital pin 2 values from the Arduino and allows sending commands.
"""

import sys
import time

import serial


def find_arduino_port():
    """Try common Arduino port names."""
    common_ports = [
        "/dev/cu.usbmodem14101",
        "/dev/cu.usbmodem141101",
        "/dev/ttyUSB0",
        "/dev/ttyACM0",
        "/dev/cu.usbserial",
    ]
    for port in common_ports:
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            print(f"Connected to Arduino on {port}")
            return ser
        except (OSError, serial.SerialException):
            continue
    return None


def main():
    # Connect to Arduino
    ser = find_arduino_port()
    if ser is None:
        print("Could not find Arduino. Please specify port manually.")
        print("Usage: python serial_comm.py [port]")
        if len(sys.argv) > 1:
            port = sys.argv[1]
            try:
                ser = serial.Serial(port, 9600, timeout=1)
                print(f"Connected to Arduino on {port}")
            except Exception as e:
                print(f"Error connecting to {port}: {e}")
                return
        else:
            return

    # Wait for Arduino to reset
    time.sleep(2)

    print("Reading from Arduino (Ctrl+C to exit)...")
    print("Type messages and press Enter to send to Arduino")
    print("-" * 50)

    try:
        while True:
            # Read from Arduino
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8").rstrip()
                print(f"Arduino: {line}")

            # Optional: uncomment to enable writing to Arduino
            # Note: This is blocking, so you won't see Arduino output while typing
            # import select
            # if select.select([sys.stdin], [], [], 0)[0]:
            #     message = sys.stdin.readline().rstrip()
            #     ser.write(f"{message}\n".encode())

    except KeyboardInterrupt:
        print("\nClosing connection...")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
