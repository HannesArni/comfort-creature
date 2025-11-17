# CAN Bus Dump Format

## Overview

This directory contains tools for capturing and parsing CAN bus data from Arduino devices. The dump format supports timestamped CAN frames and event markers for correlating system behavior with CAN traffic.

## File Format

### CAN Frame Lines

Each CAN frame is recorded on a single line with the following format:

```
[HH:MM:SS.mmm] Extended ID: 0xXXXXXXXX  DLC: N  Data: 0xXX 0xXX ...
```

**Components:**
- **Timestamp** (optional): `[HH:MM:SS.mmm]` - Time when frame was captured (millisecond precision)
- **Extended ID**: 29-bit CAN identifier in hexadecimal
- **DLC**: Data Length Code (0-8), number of data bytes
- **Data**: Space-separated hex bytes (0x00 to 0xFF format)

**Examples:**
```
[16:35:23.808] Extended ID: 0x05124504  DLC: 1  Data: 0x4F
[16:35:23.820] Extended ID: 0x03FF1504  DLC: 8  Data: 0x00 0x00 0x00 0x4F 0x00 0x00 0x00 0x00
[16:35:24.100] Extended ID: 0x02294500  DLC: 0  Data:
```

### Event Marker Lines

Events are user-inserted markers that document significant occurrences during capture:

```
# EVENT [HH:MM:SS.mmm]: description
```

**Components:**
- **Timestamp**: `[HH:MM:SS.mmm]` - Time when event was recorded
- **Description**: Free-form text describing the event

**Examples:**
```
# EVENT [16:35:34.356]: Starting unlock
# EVENT [16:35:47.892]: Motor started
# EVENT [16:36:10.100]: System stopped
```

### Comment Lines

Lines starting with `#` (except event markers) are treated as comments and ignored by the parser:

```
# This is a comment
# CAN dump captured on 2025-11-17
```

## Format Variants

The parser supports multiple format variants for backward compatibility:

1. **With timestamps** (current format):
   ```
   [16:35:23.808] Extended ID: 0x05124504  DLC: 1  Data: 0x4F
   ```

2. **Without timestamps** (legacy format):
   ```
   Extended ID: 0x05124504  DLC: 1  Data: 0x4F
   ```

3. **With trailing debug text** (automatically stripped):
   ```
   [16:35:23.808] Extended ID: 0x05124504  DLC: 1  Data: 0x4FBATTERY: 4F
   ```
   Parser extracts: `['0x4F']`

## Tools

### `capture_can_dump.py`

Captures CAN bus data from Arduino via serial port.

**Usage:**
```bash
python3 capture_can_dump.py
```

**Features:**
- Connects to `/dev/tty.usbserial-210` at 115200 baud
- Adds millisecond timestamps to each frame
- Interactive event marking: Type `e` + Enter, then describe the event
- Saves to timestamped file: `can_dump_YYYY-MM-DD_HH-MM-SS.txt`
- Graceful shutdown with Ctrl+C

**During capture:**
- Frame counter updates every 100 frames
- Press `e` + Enter to mark an event
- Enter description and press Enter to save
- Event timestamp matches when you submit the description

### `dump_parsing.py`

Parses CAN dump files into structured Python data.

**Usage as script:**
```bash
python3 dump_parsing.py
```

**Usage as library:**
```python
from dump_parsing import parse_dump_file, parse_line

# Parse entire file
entries = parse_dump_file("can_dump_2025-11-17_16-35-22.txt")

# Filter by type
frames = [e for e in entries if e["type"] == "frame"]
events = [e for e in entries if e["type"] == "event"]

# Access frame data
for frame in frames:
    print(f"ID: {frame['frame_id']}, Data: {frame['data']}")
    if "timestamp" in frame:
        print(f"  Timestamp: {frame['timestamp']}")

# Access events
for event in events:
    print(f"[{event['timestamp']}] {event['description']}")
```

**Return format:**

CAN frame entries:
```python
{
    "type": "frame",
    "frame_id": "0x05124504",
    "dlc": 1,
    "data": ["0x4F"],
    "timestamp": "16:35:23.808"  # Optional, present if captured
}
```

Event entries:
```python
{
    "type": "event",
    "timestamp": "16:35:34.356",
    "description": "Starting unlock"
}
```

### `pattern_analysis.py`

Analyzes CAN dumps for patterns and statistics.

**Usage:**
```bash
python3 pattern_analysis.py
```

**Features:**
- Identifies periodic messages (consistent timing)
- Detects static frames (unchanging data)
- Finds variable frames (changing data patterns)
- Shows frequency statistics for all frame IDs
- Summary of unique frame IDs and occurrence counts

**Note:** Currently analyzes CAN frames only. Events are preserved in the parsed data but not included in pattern analysis.

## Example Workflow

1. **Capture CAN traffic with event marking:**
   ```bash
   python3 capture_can_dump.py
   # Type 'e' + Enter when significant events occur
   # Press Ctrl+C when done
   ```

2. **Parse the dump:**
   ```python
   from dump_parsing import parse_dump_file

   entries = parse_dump_file("can_dump_2025-11-17_16-35-22.txt")
   frames = [e for e in entries if e["type"] == "frame"]
   events = [e for e in entries if e["type"] == "event"]

   print(f"Captured {len(frames)} frames and {len(events)} events")
   ```

3. **Analyze patterns:**
   ```bash
   python3 pattern_analysis.py
   ```

4. **Correlate events with CAN traffic:**
   ```python
   # Find frames around a specific event
   event_time = "16:35:34.356"

   for entry in entries:
       if entry["type"] == "event" and entry["timestamp"] == event_time:
           print(f"Event: {entry['description']}")
       elif entry["type"] == "frame" and "timestamp" in entry:
           # Check if frame is within 1 second of event
           # (implement time comparison logic as needed)
           pass
   ```

## Dependencies

- **pyserial** (3.5): Serial communication with Arduino
- **Python** (3.10+): For type hints and pattern matching

Install dependencies:
```bash
pip install -r requirements.txt
```

## Notes

- Timestamps use local system time (not synchronized with Arduino)
- Event timestamps reflect when you submit the description, not when 'e' was pressed
- Empty lines and unparseable lines are silently skipped
- The parser is backward compatible with dumps that lack timestamps
