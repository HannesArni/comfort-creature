#!/usr/bin/env python3
"""Analyze CAN bus dump for patterns."""

from collections import defaultdict
from pathlib import Path

from dump_parsing import parse_dump_file


def analyze_patterns(frames: list[dict]) -> dict:
    """Analyze CAN frames for patterns.

    Returns dict with analysis results including:
    - frame_stats: Statistics per frame ID
    - periodic_messages: Frame IDs that appear regularly
    - static_frames: Frames with unchanging data
    - variable_frames: Frames with changing data
    """
    # Group frames by ID
    frames_by_id = defaultdict(list)
    for idx, frame in enumerate(frames):
        frames_by_id[frame["frame_id"]].append({"index": idx, "data": frame["data"]})

    frame_stats = {}
    static_frames = []
    variable_frames = []

    for frame_id, occurrences in frames_by_id.items():
        count = len(occurrences)
        data_values = [tuple(occ["data"]) for occ in occurrences]
        unique_data = set(data_values)

        # Calculate intervals between occurrences
        indices = [occ["index"] for occ in occurrences]
        intervals = [indices[i + 1] - indices[i] for i in range(len(indices) - 1)]
        avg_interval = sum(intervals) / len(intervals) if intervals else 0

        stats = {
            "count": count,
            "unique_data_patterns": len(unique_data),
            "avg_interval": avg_interval,
            "is_static": len(unique_data) == 1,
            "first_occurrence": indices[0],
            "last_occurrence": indices[-1],
        }

        frame_stats[frame_id] = stats

        if stats["is_static"]:
            static_frames.append(
                {"frame_id": frame_id, "data": occurrences[0]["data"], "count": count}
            )
        else:
            variable_frames.append(
                {"frame_id": frame_id, "unique_patterns": len(unique_data)}
            )

    # Find periodic messages (consistent intervals)
    periodic_messages = []
    for frame_id, occurrences in frames_by_id.items():
        if len(occurrences) < 3:
            continue

        indices = [occ["index"] for occ in occurrences]
        intervals = [indices[i + 1] - indices[i] for i in range(len(indices) - 1)]

        # Check if intervals are consistent (within 20% variance)
        avg = sum(intervals) / len(intervals)
        variance = sum((x - avg) ** 2 for x in intervals) / len(intervals)
        std_dev = variance**0.5

        if avg > 0 and std_dev / avg < 0.2:  # Less than 20% variance
            periodic_messages.append(
                {
                    "frame_id": frame_id,
                    "avg_interval": round(avg, 1),
                    "std_dev": round(std_dev, 1),
                    "count": len(occurrences),
                }
            )

    return {
        "total_frames": len(frames),
        "unique_frame_ids": len(frames_by_id),
        "frame_stats": frame_stats,
        "static_frames": sorted(static_frames, key=lambda x: x["count"], reverse=True),
        "variable_frames": sorted(
            variable_frames, key=lambda x: x["unique_patterns"], reverse=True
        ),
        "periodic_messages": sorted(
            periodic_messages, key=lambda x: x["avg_interval"], reverse=True
        ),
    }


def print_analysis(analysis: dict):
    """Print analysis results in a readable format."""
    print("=" * 70)
    print("CAN BUS PATTERN ANALYSIS")
    print("=" * 70)
    print(f"\nTotal frames analyzed: {analysis['total_frames']}")
    print(f"Unique frame IDs: {analysis['unique_frame_ids']}")

    print("\n" + "=" * 70)
    print("PERIODIC MESSAGES (consistent timing)")
    print("=" * 70)
    if analysis["periodic_messages"]:
        for msg in analysis["periodic_messages"][:15]:
            print(
                f"{msg['frame_id']:12} - Every ~{msg['avg_interval']:6.1f} frames "
                f"(±{msg['std_dev']:.1f}), {msg['count']:4} occurrences"
            )
    else:
        print("No periodic messages detected")

    print("\n" + "=" * 70)
    print("STATIC FRAMES (unchanging data)")
    print("=" * 70)
    if analysis["static_frames"]:
        for frame in analysis["static_frames"][:15]:
            data_str = " ".join(frame["data"]) if frame["data"] else "(empty)"
            print(f"{frame['frame_id']:12} - {frame['count']:4}x - Data: {data_str}")
    else:
        print("No static frames detected")

    print("\n" + "=" * 70)
    print("VARIABLE FRAMES (changing data)")
    print("=" * 70)
    if analysis["variable_frames"]:
        for frame in analysis["variable_frames"][:15]:
            stats = analysis["frame_stats"][frame["frame_id"]]
            print(
                f"{frame['frame_id']:12} - {stats['count']:4} occurrences, "
                f"{frame['unique_patterns']:4} unique patterns"
            )
    else:
        print("No variable frames detected")

    print("\n" + "=" * 70)
    print("FRAME STATISTICS (by frequency)")
    print("=" * 70)
    sorted_stats = sorted(
        analysis["frame_stats"].items(), key=lambda x: x[1]["count"], reverse=True
    )
    for frame_id, stats in sorted_stats[:20]:
        pattern_info = (
            "static"
            if stats["is_static"]
            else f"{stats['unique_data_patterns']} patterns"
        )
        print(
            f"{frame_id:12} - {stats['count']:4}x, {pattern_info:12}, "
            f"avg interval: {stats['avg_interval']:6.1f}"
        )


if __name__ == "__main__":
    dump_file = Path(__file__).parent / "unlock-dump.txt"
    print(f"Loading {dump_file.name}...")
    frames = parse_dump_file(dump_file)

    print(f"Analyzing {len(frames)} frames...\n")
    analysis = analyze_patterns(frames)

    print_analysis(analysis)
