#!/usr/bin/env python3
"""Parse CAN bus dump from Arduino."""

import re
from pathlib import Path


def parse_line(line: str) -> dict | None:
    """Parse a single line from the dump.

    Returns dict with 'type', and type-specific keys:
    - For CAN frames: 'frame_id', 'dlc', 'data', 'timestamp' (if present)
    - For events: 'timestamp', 'description'
    Returns None if line is empty or invalid.
    """
    line = line.strip()
    if not line:
        return None

    # Check for event line
    event_pattern = r"#\s*EVENT\s*\[([^\]]+)\]:\s*(.+)"
    event_match = re.match(event_pattern, line)
    if event_match:
        return {
            "type": "event",
            "timestamp": event_match.group(1),
            "description": event_match.group(2),
        }

    # Parse optional timestamp at start
    timestamp = None
    can_line = line
    timestamp_pattern = r"^\[([^\]]+)\]\s+(.+)"
    timestamp_match = re.match(timestamp_pattern, line)
    if timestamp_match:
        timestamp = timestamp_match.group(1)
        can_line = timestamp_match.group(2)

    # Parse CAN frame (with or without data, ignore any trailing text)
    can_pattern = (
        r"Extended ID: (0x[0-9A-F]+)\s+DLC: (\d+)\s+Data:\s*((?:0x[0-9A-F]+\s*)*)"
    )
    can_match = re.match(can_pattern, can_line)

    if not can_match:
        return None

    frame_id = can_match.group(1)
    dlc = int(can_match.group(2))
    data_str = can_match.group(3).strip()
    # Only extract valid hex bytes (0xXX format)
    data_bytes = re.findall(r"0x[0-9A-F]{2}", data_str) if data_str else []

    result = {
        "type": "frame",
        "frame_id": frame_id,
        "dlc": dlc,
        "data": data_bytes,
    }

    if timestamp:
        result["timestamp"] = timestamp

    return result


def parse_dump_file(file_path: str | Path) -> list[dict]:
    """Parse entire CAN dump file and return list of parsed entries.

    Returns list of dicts with 'type' key indicating 'frame' or 'event'.
    Skips empty lines and lines that fail to parse.
    """
    entries = []

    with open(file_path) as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                entries.append(parsed)

    return entries


if __name__ == "__main__":
    dump_file = Path(__file__).parent / "unlock-dump.txt"
    entries = parse_dump_file(dump_file)

    frames = [e for e in entries if e["type"] == "frame"]
    events = [e for e in entries if e["type"] == "event"]

    print(f"Parsed {len(entries)} total entries from {dump_file.name}")
    print(f"  - {len(frames)} CAN frames")
    print(f"  - {len(events)} events")
