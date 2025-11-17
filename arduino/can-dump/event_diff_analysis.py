#!/usr/bin/env python3
"""
Analyzes CAN dump files to identify differences in messages between events.

This script helps correlate CAN traffic with user-marked events by:
- Segmenting the dump into time windows around each event
- Comparing message patterns before/after events
- Identifying messages that only appear during certain periods
- Detecting changes in message frequency or data values
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple

from dump_parsing import parse_dump_file


@dataclass
class TimeWindow:
    """Time window for analyzing CAN messages around an event."""

    start: datetime
    end: datetime
    label: str


@dataclass
class MessageStats:
    """Statistics for a specific CAN message ID in a time window."""

    frame_id: str
    count: int
    unique_data: Set[Tuple[str, ...]]  # Set of unique data patterns
    first_seen: str  # timestamp
    last_seen: str  # timestamp
    data_values: List[Tuple[str, ...]]  # All data values for averaging


def parse_timestamp(ts: str) -> datetime:
    """Parse timestamp string HH:MM:SS.mmm to datetime object."""
    # Use arbitrary date since we only care about time differences
    base_date = datetime(2025, 1, 1)
    time_parts = ts.split(":")
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds_parts = time_parts[2].split(".")
    seconds = int(seconds_parts[0])
    milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0

    return base_date.replace(
        hour=hours, minute=minutes, second=seconds, microsecond=milliseconds * 1000
    )


def create_event_windows(
    events: List[dict], before_sec: float = 2.0, after_sec: float = 5.0
) -> List[TimeWindow]:
    """
    Create time windows around each event for analysis.

    Args:
        events: List of event entries from parse_dump_file
        before_sec: Seconds before event to include
        after_sec: Seconds after event to include

    Returns:
        List of TimeWindow objects
    """
    windows = []

    for event in events:
        event_time = parse_timestamp(event["timestamp"])
        start = event_time - timedelta(seconds=before_sec)
        end = event_time + timedelta(seconds=after_sec)

        windows.append(
            TimeWindow(
                start=start,
                end=end,
                label=f"{event['timestamp']}: {event['description']}",
            )
        )

    return windows


def create_event_to_event_windows(events: List[dict]) -> List[TimeWindow]:
    """
    Create time windows between consecutive events.

    Args:
        events: List of event entries from parse_dump_file

    Returns:
        List of TimeWindow objects, one for each pair of consecutive events
    """
    windows = []

    for i in range(len(events) - 1):
        start_event = events[i]
        end_event = events[i + 1]

        start_time = parse_timestamp(start_event["timestamp"])
        end_time = parse_timestamp(end_event["timestamp"])

        windows.append(
            TimeWindow(
                start=start_time,
                end=end_time,
                label=f"Between '{start_event['description']}' and '{end_event['description']}'",
            )
        )

    return windows


def analyze_window(frames: List[dict], window: TimeWindow) -> Dict[str, MessageStats]:
    """
    Analyze CAN frames within a specific time window.

    Args:
        frames: List of frame entries from parse_dump_file
        window: TimeWindow to analyze

    Returns:
        Dictionary mapping frame_id to MessageStats
    """
    stats: Dict[str, MessageStats] = {}

    for frame in frames:
        if "timestamp" not in frame:
            continue

        frame_time = parse_timestamp(frame["timestamp"])

        if window.start <= frame_time <= window.end:
            frame_id = frame["frame_id"]
            data_tuple = tuple(frame["data"])

            if frame_id not in stats:
                stats[frame_id] = MessageStats(
                    frame_id=frame_id,
                    count=0,
                    unique_data=set(),
                    first_seen=frame["timestamp"],
                    last_seen=frame["timestamp"],
                    data_values=[],
                )

            stats[frame_id].count += 1
            stats[frame_id].unique_data.add(data_tuple)
            stats[frame_id].last_seen = frame["timestamp"]
            stats[frame_id].data_values.append(data_tuple)

    return stats


def calculate_average_data(data_values: List[Tuple[str, ...]]) -> List[float]:
    """
    Calculate average value for each byte position across all data values.

    Args:
        data_values: List of data tuples (e.g., [('0x4F', '0x00'), ('0x50', '0x01')])

    Returns:
        List of average values, one per byte position
    """
    if not data_values:
        return []

    # Find the maximum data length
    max_len = max(len(d) for d in data_values)
    if max_len == 0:
        return []

    averages = []
    for byte_pos in range(max_len):
        values = []
        for data_tuple in data_values:
            if byte_pos < len(data_tuple):
                try:
                    # Convert hex string to int
                    val = int(data_tuple[byte_pos], 16)
                    values.append(val)
                except (ValueError, TypeError):
                    pass

        if values:
            averages.append(sum(values) / len(values))
        else:
            averages.append(0.0)

    return averages


def compare_windows(
    window1: TimeWindow,
    stats1: Dict[str, MessageStats],
    window2: TimeWindow,
    stats2: Dict[str, MessageStats],
) -> None:
    """
    Compare two time windows and print differences.

    Args:
        window1: First time window
        stats1: Statistics for first window
        window2: Second time window
        stats2: Statistics for second window
    """
    print(f"\n{'=' * 80}")
    print("COMPARISON:")
    print(f"  Window 1: {window1.label}")
    print(f"  Window 2: {window2.label}")
    print(f"{'=' * 80}\n")

    ids1 = set(stats1.keys())
    ids2 = set(stats2.keys())

    # Messages only in window 1
    only_in_1 = ids1 - ids2
    if only_in_1:
        print(f"Messages only in window 1 ({len(only_in_1)}):")
        for frame_id in sorted(only_in_1):
            stat = stats1[frame_id]
            print(f"  {frame_id}: {stat.count} occurrences")
        print()

    # Messages only in window 2
    only_in_2 = ids2 - ids1
    if only_in_2:
        print(f"Messages only in window 2 ({len(only_in_2)}):")
        for frame_id in sorted(only_in_2):
            stat = stats2[frame_id]
            print(f"  {frame_id}: {stat.count} occurrences")
        print()

    # Messages in both - compare frequency and data
    common = ids1 & ids2
    if common:
        print(f"Messages in both windows ({len(common)}):")
        print(
            f"{'ID':<15} {'Count W1':>10} {'Count W2':>10} {'Δ Count':>10} "
            f"{'Data Changed':>12} {'Avg Changed':>12}"
        )
        print(f"{'-' * 82}")

        for frame_id in sorted(common):
            stat1 = stats1[frame_id]
            stat2 = stats2[frame_id]

            count_diff = stat2.count - stat1.count
            data_changed = stat1.unique_data != stat2.unique_data

            # Calculate average values
            avg1 = calculate_average_data(stat1.data_values)
            avg2 = calculate_average_data(stat2.data_values)

            # Check if averages differ significantly (> 1.0 difference in any byte)
            avg_changed = False
            if len(avg1) == len(avg2):
                for a1, a2 in zip(avg1, avg2):
                    if abs(a1 - a2) > 1.0:
                        avg_changed = True
                        break
            else:
                avg_changed = True  # Different lengths

            print(
                f"{frame_id:<15} {stat1.count:>10} {stat2.count:>10} "
                f"{count_diff:>10} {str(data_changed):>12} {str(avg_changed):>12}"
            )

            # Show data differences if they exist
            if data_changed:
                only_in_stat1 = stat1.unique_data - stat2.unique_data
                only_in_stat2 = stat2.unique_data - stat1.unique_data

                if only_in_stat1:
                    print(f"    Data only in W1: {list(only_in_stat1)[:3]}")
                if only_in_stat2:
                    print(f"    Data only in W2: {list(only_in_stat2)[:3]}")

            # Show average differences if significant
            if avg_changed and len(avg1) == len(avg2):
                print(f"    Avg W1: {[f'{a:.1f}' for a in avg1]}")
                print(f"    Avg W2: {[f'{a:.1f}' for a in avg2]}")
                diffs = [a2 - a1 for a1, a2 in zip(avg1, avg2)]
                print(f"    Δ Avg:  {[f'{d:+.1f}' for d in diffs]}")

        print()


def analyze_baseline_vs_event(
    frames: List[dict],
    events: List[dict],
    baseline_start_event: str = None,
    baseline_end_event: str = None,
) -> None:
    """
    Compare a baseline period with all other event-to-event periods.

    Args:
        frames: List of frame entries
        events: List of event entries
        baseline_start_event: Description substring of event marking baseline start
        baseline_end_event: Description substring of event marking baseline end
    """
    if not events:
        print("No events found in dump file.")
        return

    # Create all event-to-event windows
    all_windows = create_event_to_event_windows(events)

    # Find baseline window if specified
    baseline_window = None
    if baseline_start_event and baseline_end_event:
        for window in all_windows:
            if (
                baseline_start_event.lower() in window.label.lower()
                and baseline_end_event.lower() in window.label.lower()
            ):
                baseline_window = window
                break

        if not baseline_window:
            print(
                f"Warning: Could not find baseline window containing "
                f"'{baseline_start_event}' and '{baseline_end_event}'"
            )
            print("Available windows:")
            for i, window in enumerate(all_windows):
                print(f"  {i}: {window.label}")
            return
    else:
        # Default: use first event-to-event window
        if all_windows:
            baseline_window = all_windows[0]
        else:
            print("No event-to-event windows available.")
            return

    baseline_stats = analyze_window(frames, baseline_window)

    print(f"\n{'=' * 80}")
    print("BASELINE ANALYSIS")
    print(f"{'=' * 80}")
    print(f"Label: {baseline_window.label}")
    print(f"Unique message IDs: {len(baseline_stats)}")
    print(f"Total messages: {sum(stat.count for stat in baseline_stats.values())}")

    # Compare baseline with all other windows
    for window in all_windows:
        if window == baseline_window:
            continue  # Skip comparing baseline to itself
        event_stats = analyze_window(frames, window)
        compare_windows(baseline_window, baseline_stats, window, event_stats)


def main():
    """Main entry point."""
    import sys

    # Parse command line arguments
    dump_file = "can_dump_2025-11-17_16-35-22.txt"
    baseline_start = None
    baseline_end = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--baseline-start" and i + 1 < len(sys.argv):
            baseline_start = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--baseline-end" and i + 1 < len(sys.argv):
            baseline_end = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] in ["-h", "--help"]:
            print("Usage: python3 event_diff_analysis.py [dump_file] [options]")
            print()
            print("Options:")
            print(
                "  --baseline-start TEXT  Event description substring for baseline start"
            )
            print(
                "  --baseline-end TEXT    Event description substring for baseline end"
            )
            print()
            print("Example:")
            print(
                "  python3 event_diff_analysis.py --baseline-start 'Unlocked' "
                "--baseline-end 'Going to try'"
            )
            return
        else:
            dump_file = sys.argv[i]
            i += 1

    print(f"Analyzing CAN dump: {dump_file}")
    print()

    entries = parse_dump_file(dump_file)

    frames = [e for e in entries if e["type"] == "frame"]
    events = [e for e in entries if e["type"] == "event"]

    print(f"Loaded {len(frames)} frames and {len(events)} events")

    if not events:
        print(
            "\nNo events found. Use capture_can_dump.py to mark events during capture."
        )
        return

    if not any("timestamp" in f for f in frames):
        print(
            "\nWarning: No timestamps found in frames. "
            "Analysis requires timestamped dumps."
        )
        return

    # Show available events
    print("\nAvailable events:")
    for i, event in enumerate(events):
        print(f"  {i}: [{event['timestamp']}] {event['description']}")
    print()

    # Perform baseline vs event analysis
    analyze_baseline_vs_event(frames, events, baseline_start, baseline_end)

    # Compare consecutive event windows (between events)
    print(f"\n\n{'=' * 80}")
    print("EVENT-TO-EVENT WINDOW COMPARISONS")
    print(f"{'=' * 80}\n")

    event_windows = create_event_to_event_windows(events)
    for i in range(len(event_windows) - 1):
        w1 = event_windows[i]
        w2 = event_windows[i + 1]
        stats1 = analyze_window(frames, w1)
        stats2 = analyze_window(frames, w2)
        compare_windows(w1, stats1, w2, stats2)


if __name__ == "__main__":
    main()
