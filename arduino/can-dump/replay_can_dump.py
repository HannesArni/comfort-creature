#!/usr/bin/env python3
"""
CAN Message Replay Script

Replays CAN messages from a dump file between two event markers,
maintaining original timing and displaying incoming serial data.
"""

import threading
import time
from datetime import datetime
from typing import List

import serial
from dump_parsing import parse_dump_file

PORT = "/dev/ttyUSB1"
BAUD_RATE = 115200
START_BYTE = 0xAA

# Event markers to filter between
START_EVENT = "Unlocked"
END_EVENT = "Going to try moving throttle"


def parse_timestamp(timestamp_str: str) -> float:
    """Convert HH:MM:SS.mmm timestamp to seconds since midnight."""
    time_obj = datetime.strptime(timestamp_str, "%H:%M:%S.%f")
    return (
        time_obj.hour * 3600
        + time_obj.minute * 60
        + time_obj.second
        + time_obj.microsecond / 1_000_000
    )


def create_can_frame(frame_id: str, data: List[str]) -> bytes:
    """
    Create a CAN frame in the format expected by Arduino.

    Format: [start_byte (1)] [frame_id (4)] [data (8)]
    """
    # Parse frame ID (e.g., "0x05124504" -> 0x05124504)
    id_int = int(frame_id, 16)

    # Parse data bytes and pad to 8 bytes
    data_bytes = [int(byte, 16) for byte in data]
    # Pad with zeros if less than 8 bytes
    while len(data_bytes) < 8:
        data_bytes.append(0x00)

    # Build frame
    frame = (
        START_BYTE.to_bytes(1, byteorder="big")
        + id_int.to_bytes(4, byteorder="big")
        + bytes(data_bytes[:8])  # Ensure exactly 8 bytes
    )

    return frame


def serial_reader_thread(ser: serial.Serial, stop_event: threading.Event):
    """Background thread to continuously read and display incoming serial data."""
    while not stop_event.is_set():
        try:
            if ser.in_waiting > 0:
                line = ser.readline()
                if line:
                    decoded = line.decode(errors="ignore").strip()
                    if decoded:
                        print(f"  Arduino: {decoded}")
        except Exception as e:
            if not stop_event.is_set():
                print(f"  Serial read error: {e}")
        time.sleep(0.01)  # Small delay to avoid busy-waiting


def replay_can_messages(
    dump_file: str,
    port: str = PORT,
    baud_rate: int = BAUD_RATE,
    start_event: str = START_EVENT,
    end_event: str = END_EVENT,
):
    """Replay CAN messages between two events from a dump file."""
    print(f"Parsing dump file: {dump_file}")
    entries = parse_dump_file(dump_file)

    # Find event boundaries
    start_idx = None
    end_idx = None

    for i, entry in enumerate(entries):
        if entry["type"] == "event":
            if start_event.lower() in entry["description"].lower():
                start_idx = i
                print(f"Found start event at line {i}: {entry['description']}")
            elif end_event.lower() in entry["description"].lower():
                end_idx = i
                print(f"Found end event at line {i}: {entry['description']}")
                break

    if start_idx is None:
        print(f"ERROR: Could not find start event containing '{start_event}'")
        return
    if end_idx is None:
        print(f"ERROR: Could not find end event containing '{end_event}'")
        return

    # Extract frames between events
    frames = [
        entry
        for entry in entries[start_idx + 1 : end_idx]
        if entry["type"] == "frame" and "timestamp" in entry
    ]

    if not frames:
        print("ERROR: No frames with timestamps found between events")
        return

    print(f"\nFound {len(frames)} frames to replay")
    print(f"Time span: {frames[0]['timestamp']} to {frames[-1]['timestamp']}")

    # Open serial connection
    print(f"\nConnecting to {port} at {baud_rate} baud...")
    ser = serial.Serial(port, baud_rate, timeout=1)
    print("Waiting 2 seconds for Arduino to reset...")
    time.sleep(2)

    # Start serial reader thread
    stop_event = threading.Event()
    reader = threading.Thread(target=serial_reader_thread, args=(ser, stop_event))
    reader.daemon = True
    reader.start()

    print("\nStarting replay...\n")

    try:
        while True:
            start_time = parse_timestamp(frames[0]["timestamp"])
            replay_start = time.time()

            for i, frame in enumerate(frames):
                # Calculate when this frame should be sent
                frame_time = parse_timestamp(frame["timestamp"])
                delay_since_start = frame_time - start_time

                # Wait until it's time to send this frame
                elapsed = time.time() - replay_start
                sleep_time = delay_since_start - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

                # Create and send frame
                can_frame = create_can_frame(frame["frame_id"], frame["data"])
                ser.write(can_frame)

                # Progress indicator every 100 frames
                if (i + 1) % 100 == 0:
                    progress = (i + 1) / len(frames) * 100
                    print(
                        f"Progress: {i + 1}/{len(frames)} frames ({progress:.1f}%) "
                        f"- ID: {frame['frame_id']}"
                    )

            print(f"\nReplay complete! Sent {len(frames)} frames")

            # Wait a bit for any final responses
            print("\nWaiting 2 seconds for final responses...")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\nReplay interrupted by user")
    finally:
        stop_event.set()
        reader.join(timeout=1)
        ser.close()
        print("Serial connection closed")


def main():
    dump_file = "can_dump_2025-11-17_16-35-22.txt"
    replay_can_messages(dump_file)


if __name__ == "__main__":
    main()
