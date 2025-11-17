#!/usr/bin/env python3
"""Capture CAN bus data from Arduino via serial with event marking."""

import sys
import threading
from datetime import datetime
from pathlib import Path

import serial


class CANCapture:
    """Capture CAN frames from serial port with event marking."""

    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.output_file = None
        self.frame_count = 0
        self.event_count = 0
        self.running = False
        self.event_pending = False

    def connect(self):
        """Connect to serial port."""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")
            return False

    def start_capture(self, output_path: Path):
        """Start capturing CAN frames to file."""
        self.output_file = open(output_path, "w", buffering=1)
        self.running = True
        self.frame_count = 0
        self.event_count = 0

        print(f"\nCapturing to: {output_path}")
        print("=" * 70)
        print("Press 'e' + Enter to mark an event")
        print("Press Ctrl+C to stop\n")

        # Start keyboard input thread
        input_thread = threading.Thread(target=self._handle_input, daemon=True)
        input_thread.start()

        # Main capture loop
        try:
            while self.running:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode("utf-8", errors="ignore").strip()

                    if line:
                        # Add timestamp and write frame to file
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        timestamped_line = f"[{timestamp}] {line}"
                        self.output_file.write(timestamped_line + "\n")
                        self.frame_count += 1

                        # Update display every 100 frames
                        if self.frame_count % 100 == 0:
                            self._print_status()

                # Check for pending event
                if self.event_pending:
                    self._mark_event()
                    self.event_pending = False

        except KeyboardInterrupt:
            print("\n\nStopping capture...")
        finally:
            self.running = False
            self._cleanup()

    def _handle_input(self):
        """Handle keyboard input in separate thread."""
        while self.running:
            try:
                user_input = input()
                if user_input.lower() == "e":
                    self.event_pending = True
            except EOFError:
                break

    def _mark_event(self):
        """Mark an event in the capture."""
        print("\nEnter event description: ", end="", flush=True)
        try:
            description = input()
            if description:
                # Capture timestamp when description is submitted
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                event_line = f"# EVENT [{timestamp}]: {description}"
                self.output_file.write(event_line + "\n")
                self.event_count += 1
                print(f"✓ Event marked at [{timestamp}]: {description}\n")
            else:
                print("Event cancelled (empty description)\n")
        except EOFError:
            print("Event cancelled\n")

        self._print_status()

    def _print_status(self):
        """Print current capture status."""
        print(
            f"Frames captured: {self.frame_count:6} | Events: {self.event_count}",
            end="\r",
            flush=True,
        )

    def _cleanup(self):
        """Clean up resources."""
        if self.output_file:
            self.output_file.close()
            print("\n\nCapture complete!")
            print("=" * 70)
            print(f"Total frames: {self.frame_count}")
            print(f"Total events: {self.event_count}")
            print(f"Output file: {self.output_file.name}")

        if self.ser and self.ser.is_open:
            self.ser.close()


def main():
    """Main entry point."""
    port = "/dev/tty.usbserial-210"
    baudrate = 115200

    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = Path(__file__).parent / f"can_dump_{timestamp}.txt"

    # Create capture instance
    capture = CANCapture(port, baudrate)

    # Connect to serial port
    if not capture.connect():
        sys.exit(1)

    # Start capture
    try:
        capture.start_capture(output_path)
    except Exception as e:
        print(f"\nError during capture: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
