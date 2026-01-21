#!/usr/bin/env python3
"""
Video to Frames Processor

Converts video recordings into timestamped screenshots mapped to transcript segments.
Designed for Claude Code analysis of video content.

Usage:
    python video_processor.py <video_file> <transcript_file> [--output-dir <dir>]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class TranscriptSegment:
    """Represents a segment of transcript with timing information."""
    start_seconds: float
    end_seconds: float
    text: str
    speaker_id: Optional[str] = None
    speaker_name: Optional[str] = None


@dataclass
class SpeakerSegment:
    """Represents a speaker turn with timing and content."""
    speaker_id: str
    speaker_name: Optional[str]
    start_seconds: float
    end_seconds: float
    text: str
    word_count: int


@dataclass
class SpeakerMetrics:
    """Metrics for a single speaker."""
    speaker_id: str
    speaker_name: Optional[str]
    talk_time_seconds: float
    talk_time_pct: float
    word_count: int
    speaking_pace_wpm: float
    turn_count: int
    avg_turn_length_seconds: float


@dataclass
class Frame:
    """Represents an extracted frame with associated metadata."""
    timestamp: str
    timestamp_seconds: float
    screenshot: str
    transcript_segment: str
    speaker_id: Optional[str] = None


def parse_timestamp(ts: str) -> float:
    """Convert various timestamp formats to seconds."""
    ts = ts.strip()

    # Handle HH:MM:SS,mmm or HH:MM:SS.mmm (SRT/VTT format)
    match = re.match(r'(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})', ts)
    if match:
        h, m, s, ms = map(int, match.groups())
        return h * 3600 + m * 60 + s + ms / 1000

    # Handle HH:MM:SS
    match = re.match(r'(\d{1,2}):(\d{2}):(\d{2})', ts)
    if match:
        h, m, s = map(int, match.groups())
        return h * 3600 + m * 60 + s

    # Handle MM:SS.mmm or MM:SS,mmm
    match = re.match(r'(\d{1,2}):(\d{2})[,.](\d{3})', ts)
    if match:
        m, s, ms = map(int, match.groups())
        return m * 60 + s + ms / 1000

    # Handle MM:SS
    match = re.match(r'(\d{1,2}):(\d{2})', ts)
    if match:
        m, s = map(int, match.groups())
        return m * 60 + s

    # Handle seconds only
    try:
        return float(ts)
    except ValueError:
        return 0.0


def seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def extract_speaker_from_vtt_line(line: str) -> tuple[Optional[str], str]:
    """Extract speaker name from VTT voice tag and return (speaker, cleaned_text)."""
    # Match <v Speaker Name>text</v> or <v Speaker Name>text
    voice_match = re.match(r'<v\s+([^>]+)>(.*)(?:</v>)?', line)
    if voice_match:
        speaker = voice_match.group(1).strip()
        text = voice_match.group(2).strip()
        # Remove any remaining tags
        text = re.sub(r'<[^>]+>', '', text)
        return speaker, text

    # Match "Speaker Name: text" pattern
    speaker_colon_match = re.match(r'^([^:]+):\s*(.+)$', line)
    if speaker_colon_match:
        potential_speaker = speaker_colon_match.group(1).strip()
        # Heuristic: speaker names are usually 1-4 words
        if len(potential_speaker.split()) <= 4 and not any(c.isdigit() for c in potential_speaker):
            return potential_speaker, speaker_colon_match.group(2).strip()

    # Remove any remaining VTT tags
    cleaned = re.sub(r'<[^>]+>', '', line)
    return None, cleaned


def parse_vtt(content: str) -> list[TranscriptSegment]:
    """Parse WebVTT format transcript with speaker detection."""
    segments = []
    lines = content.strip().split('\n')

    i = 0
    # Skip WEBVTT header
    while i < len(lines) and not re.match(r'\d{2}:\d{2}', lines[i]):
        i += 1

    speaker_counter = {}  # Track speaker IDs

    while i < len(lines):
        line = lines[i].strip()

        # Look for timestamp line: 00:00:00.000 --> 00:00:05.000
        match = re.match(r'([\d:,.]+)\s*-->\s*([\d:,.]+)', line)
        if match:
            start = parse_timestamp(match.group(1))
            end = parse_timestamp(match.group(2))

            # Collect text lines until empty line or next timestamp
            text_lines = []
            segment_speaker = None
            i += 1
            while i < len(lines):
                text_line = lines[i].strip()
                if not text_line or re.match(r'([\d:,.]+)\s*-->\s*([\d:,.]+)', text_line):
                    break
                # Skip cue identifiers (numeric or NOTE)
                if not re.match(r'^\d+$', text_line) and not text_line.startswith('NOTE'):
                    speaker, cleaned_text = extract_speaker_from_vtt_line(text_line)
                    if speaker and not segment_speaker:
                        segment_speaker = speaker
                    if cleaned_text:
                        text_lines.append(cleaned_text)
                i += 1

            if text_lines:
                # Assign speaker ID
                speaker_id = None
                if segment_speaker:
                    if segment_speaker not in speaker_counter:
                        speaker_counter[segment_speaker] = f"speaker_{len(speaker_counter) + 1}"
                    speaker_id = speaker_counter[segment_speaker]

                segments.append(TranscriptSegment(
                    start_seconds=start,
                    end_seconds=end,
                    text=' '.join(text_lines),
                    speaker_id=speaker_id,
                    speaker_name=segment_speaker
                ))
        else:
            i += 1

    return segments


def parse_srt(content: str) -> list[TranscriptSegment]:
    """Parse SRT format transcript with speaker detection."""
    segments = []
    blocks = re.split(r'\n\s*\n', content.strip())
    speaker_counter = {}

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue

        # Find timestamp line
        for i, line in enumerate(lines):
            match = re.match(r'([\d:,.]+)\s*-->\s*([\d:,.]+)', line)
            if match:
                start = parse_timestamp(match.group(1))
                end = parse_timestamp(match.group(2))
                text_lines = lines[i+1:]

                # Check for speaker in text
                segment_speaker = None
                cleaned_lines = []
                for text_line in text_lines:
                    # Remove HTML-like tags first
                    text_line = re.sub(r'<[^>]+>', '', text_line)

                    # Check for "Speaker: text" pattern
                    speaker_match = re.match(r'^([^:]+):\s*(.+)$', text_line)
                    if speaker_match:
                        potential_speaker = speaker_match.group(1).strip()
                        if len(potential_speaker.split()) <= 4 and not any(c.isdigit() for c in potential_speaker):
                            if not segment_speaker:
                                segment_speaker = potential_speaker
                            cleaned_lines.append(speaker_match.group(2).strip())
                            continue
                    cleaned_lines.append(text_line)

                text = ' '.join(cleaned_lines).strip()

                # Assign speaker ID
                speaker_id = None
                if segment_speaker:
                    if segment_speaker not in speaker_counter:
                        speaker_counter[segment_speaker] = f"speaker_{len(speaker_counter) + 1}"
                    speaker_id = speaker_counter[segment_speaker]

                segments.append(TranscriptSegment(
                    start_seconds=start,
                    end_seconds=end,
                    text=text,
                    speaker_id=speaker_id,
                    speaker_name=segment_speaker
                ))
                break

    return segments


def parse_plain_text(content: str) -> list[TranscriptSegment]:
    """Parse plain text transcript with timestamps and speaker detection."""
    segments = []
    lines = content.strip().split('\n')
    speaker_counter = {}

    # Pattern 1: [00:00:00] Text or (00:00:00) Text
    # Pattern 2: 00:00:00 - Text or 00:00:00: Text
    # Pattern 3: Speaker [00:00:00]: Text
    # Pattern 4: [00:00:00] Speaker: Text

    timestamp_patterns = [
        (r'^([A-Za-z][^[\]()]*?)\s*[\[\(]([\d:,.]+)[\]\)]:\s*(.+)$', 'speaker_first'),  # Speaker [00:00:00]: Text
        (r'^[\[\(]([\d:,.]+)[\]\)]\s*([A-Za-z][^:]*?):\s*(.+)$', 'ts_speaker'),  # [00:00:00] Speaker: Text
        (r'^[\[\(]([\d:,.]+)[\]\)]\s*(.+)$', 'ts_only'),  # [00:00:00] Text
        (r'^([\d:,.]+)\s*[-:]\s*(.+)$', 'ts_dash'),  # 00:00:00 - Text
    ]

    parsed_items = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        for pattern, pattern_type in timestamp_patterns:
            match = re.match(pattern, line)
            if match:
                if pattern_type == 'speaker_first':
                    speaker = match.group(1).strip()
                    ts = parse_timestamp(match.group(2))
                    text = match.group(3).strip()
                elif pattern_type == 'ts_speaker':
                    ts = parse_timestamp(match.group(1))
                    speaker = match.group(2).strip()
                    text = match.group(3).strip()
                elif pattern_type in ('ts_only', 'ts_dash'):
                    ts = parse_timestamp(match.group(1))
                    text = match.group(2).strip()
                    # Check if text starts with "Speaker: "
                    speaker_in_text = re.match(r'^([A-Za-z][^:]*?):\s*(.+)$', text)
                    if speaker_in_text:
                        potential_speaker = speaker_in_text.group(1).strip()
                        if len(potential_speaker.split()) <= 4:
                            speaker = potential_speaker
                            text = speaker_in_text.group(2).strip()
                        else:
                            speaker = None
                    else:
                        speaker = None

                parsed_items.append((ts, text, speaker))
                break

    # Convert to segments with estimated end times
    for i, (start, text, speaker) in enumerate(parsed_items):
        if i + 1 < len(parsed_items):
            end = parsed_items[i + 1][0]
        else:
            end = start + 10  # Assume 10 second duration for last segment

        # Assign speaker ID
        speaker_id = None
        if speaker:
            if speaker not in speaker_counter:
                speaker_counter[speaker] = f"speaker_{len(speaker_counter) + 1}"
            speaker_id = speaker_counter[speaker]

        segments.append(TranscriptSegment(
            start_seconds=start,
            end_seconds=end,
            text=text,
            speaker_id=speaker_id,
            speaker_name=speaker
        ))

    return segments


def parse_transcript(file_path: str) -> list[TranscriptSegment]:
    """Parse transcript file, auto-detecting format."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    ext = Path(file_path).suffix.lower()

    if ext == '.vtt':
        return parse_vtt(content)
    elif ext == '.srt':
        return parse_srt(content)
    else:
        # Try to detect format from content
        if content.strip().startswith('WEBVTT'):
            return parse_vtt(content)
        elif re.search(r'^\d+\s*\n[\d:,]+\s*-->', content, re.MULTILINE):
            return parse_srt(content)
        else:
            return parse_plain_text(content)


def compute_speaker_metrics(segments: list[TranscriptSegment]) -> tuple[list[SpeakerMetrics], list[SpeakerSegment], int]:
    """Compute speaker-level metrics from transcript segments.

    Returns:
        - List of SpeakerMetrics (one per speaker)
        - List of SpeakerSegments (consolidated turns)
        - Total turn count
    """
    if not segments:
        return [], [], 0

    # Build speaker segments (consolidate consecutive segments from same speaker)
    speaker_segments: list[SpeakerSegment] = []
    current_speaker = None
    current_start = 0.0
    current_end = 0.0
    current_text_parts = []

    for seg in segments:
        speaker = seg.speaker_id or "unknown"
        speaker_name = seg.speaker_name

        if speaker != current_speaker:
            # Save previous segment if exists
            if current_text_parts:
                text = ' '.join(current_text_parts)
                speaker_segments.append(SpeakerSegment(
                    speaker_id=current_speaker or "unknown",
                    speaker_name=current_speaker_name,
                    start_seconds=current_start,
                    end_seconds=current_end,
                    text=text,
                    word_count=len(text.split())
                ))
            # Start new segment
            current_speaker = speaker
            current_speaker_name = speaker_name
            current_start = seg.start_seconds
            current_end = seg.end_seconds
            current_text_parts = [seg.text]
        else:
            # Continue current segment
            current_end = seg.end_seconds
            current_text_parts.append(seg.text)

    # Don't forget the last segment
    if current_text_parts:
        text = ' '.join(current_text_parts)
        speaker_segments.append(SpeakerSegment(
            speaker_id=current_speaker or "unknown",
            speaker_name=current_speaker_name if current_speaker else None,
            start_seconds=current_start,
            end_seconds=current_end,
            text=text,
            word_count=len(text.split())
        ))

    # Compute metrics per speaker
    speaker_data = {}  # speaker_id -> {talk_time, word_count, turns, speaker_name}

    for seg in speaker_segments:
        if seg.speaker_id not in speaker_data:
            speaker_data[seg.speaker_id] = {
                'talk_time': 0.0,
                'word_count': 0,
                'turns': 0,
                'speaker_name': seg.speaker_name
            }
        duration = seg.end_seconds - seg.start_seconds
        speaker_data[seg.speaker_id]['talk_time'] += duration
        speaker_data[seg.speaker_id]['word_count'] += seg.word_count
        speaker_data[seg.speaker_id]['turns'] += 1

    # Calculate totals
    total_talk_time = sum(d['talk_time'] for d in speaker_data.values())
    total_turns = sum(d['turns'] for d in speaker_data.values())

    # Build metrics list
    metrics = []
    for speaker_id, data in speaker_data.items():
        talk_time = data['talk_time']
        word_count = data['word_count']
        turns = data['turns']

        metrics.append(SpeakerMetrics(
            speaker_id=speaker_id,
            speaker_name=data['speaker_name'],
            talk_time_seconds=round(talk_time, 2),
            talk_time_pct=round((talk_time / total_talk_time * 100) if total_talk_time > 0 else 0, 1),
            word_count=word_count,
            speaking_pace_wpm=round((word_count / talk_time * 60) if talk_time > 0 else 0, 1),
            turn_count=turns,
            avg_turn_length_seconds=round(talk_time / turns if turns > 0 else 0, 2)
        ))

    # Sort by talk time descending
    metrics.sort(key=lambda m: m.talk_time_seconds, reverse=True)

    return metrics, speaker_segments, total_turns


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def extract_baseline_frames(video_path: str, output_dir: str, interval: float = 5.0) -> list[tuple[float, str]]:
    """Extract frames at regular intervals."""
    frames = []
    duration = get_video_duration(video_path)

    print(f"Video duration: {seconds_to_timestamp(duration)} ({duration:.1f}s)")
    print(f"Extracting baseline frames every {interval}s...")

    # Use ffmpeg to extract frames at interval
    output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')
    cmd = [
        'ffmpeg', '-y', '-i', video_path,
        '-vf', f'fps=1/{interval}',
        '-q:v', '2',  # High quality JPEG
        output_pattern
    ]

    subprocess.run(cmd, capture_output=True)

    # Collect extracted frame info
    frame_num = 1
    timestamp = 0.0
    while timestamp < duration:
        filename = f'frame_{frame_num:04d}.jpg'
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            frames.append((timestamp, filename))
        frame_num += 1
        timestamp += interval

    print(f"Extracted {len(frames)} baseline frames")
    return frames


def detect_scene_changes(video_path: str, output_dir: str, threshold: float = 0.3) -> list[tuple[float, str]]:
    """Detect and extract frames at scene changes using ffmpeg."""
    print(f"Detecting scene changes (threshold: {threshold})...")

    # First, get scene change timestamps
    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f"select='gt(scene,{threshold})',showinfo",
        '-f', 'null', '-'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse scene change timestamps from stderr
    scene_times = []
    for line in result.stderr.split('\n'):
        match = re.search(r'pts_time:([\d.]+)', line)
        if match:
            scene_times.append(float(match.group(1)))

    print(f"Detected {len(scene_times)} scene changes")

    # Extract frames at scene change points
    frames = []
    for i, timestamp in enumerate(scene_times):
        filename = f'scene_{i:04d}.jpg'
        filepath = os.path.join(output_dir, filename)

        cmd = [
            'ffmpeg', '-y', '-ss', str(timestamp),
            '-i', video_path,
            '-frames:v', '1',
            '-q:v', '2',
            filepath
        ]
        subprocess.run(cmd, capture_output=True)

        if os.path.exists(filepath):
            frames.append((timestamp, filename))

    print(f"Extracted {len(frames)} scene change frames")
    return frames


def merge_frames(baseline: list[tuple[float, str]],
                 scene_changes: list[tuple[float, str]],
                 min_gap: float = 2.0) -> list[tuple[float, str]]:
    """Merge baseline and scene change frames, removing duplicates."""
    all_frames = baseline + scene_changes
    all_frames.sort(key=lambda x: x[0])

    merged = []
    last_time = -min_gap

    for timestamp, filename in all_frames:
        if timestamp - last_time >= min_gap:
            merged.append((timestamp, filename))
            last_time = timestamp

    return merged


def find_transcript_segment(timestamp: float, segments: list[TranscriptSegment]) -> tuple[str, Optional[str], Optional[str]]:
    """Find the transcript segment active at a given timestamp.

    Returns:
        Tuple of (text, speaker_id, speaker_name)
    """
    for segment in segments:
        if segment.start_seconds <= timestamp <= segment.end_seconds:
            return segment.text, segment.speaker_id, segment.speaker_name

    # Find closest segment if no exact match
    closest = None
    min_diff = float('inf')

    for segment in segments:
        diff = abs(segment.start_seconds - timestamp)
        if diff < min_diff:
            min_diff = diff
            closest = segment

    if closest and min_diff < 10:  # Within 10 seconds
        return closest.text, closest.speaker_id, closest.speaker_name

    return "[No transcript available]", None, None


def process_video(video_path: str, transcript_path: str, output_dir: Optional[str] = None,
                  frame_interval: float = 5.0, scene_threshold: float = 0.3,
                  target_frames: int = 500) -> dict:
    """Main processing function."""

    # Setup paths
    video_path = os.path.abspath(video_path)
    transcript_path = os.path.abspath(transcript_path)
    video_name = Path(video_path).stem

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(video_path), 'output', video_name)

    frames_dir = os.path.join(output_dir, 'frames')
    os.makedirs(frames_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Video to Frames Processor")
    print(f"{'='*60}")
    print(f"Video: {video_path}")
    print(f"Transcript: {transcript_path}")
    print(f"Output: {output_dir}")
    print(f"{'='*60}\n")

    # Parse transcript
    print("Parsing transcript...")
    segments = parse_transcript(transcript_path)
    print(f"Found {len(segments)} transcript segments")

    if not segments:
        print("Warning: No transcript segments found!")

    # Compute speaker metrics
    print("Computing speaker metrics...")
    speaker_metrics, speaker_segments, total_turns = compute_speaker_metrics(segments)

    # Count unique speakers
    speakers_with_names = [m for m in speaker_metrics if m.speaker_name]
    print(f"Detected {len(speaker_metrics)} speakers, {len(speakers_with_names)} with names, {total_turns} turns")

    # Extract baseline frames
    baseline_frames = extract_baseline_frames(video_path, frames_dir, frame_interval)

    # Detect and extract scene changes
    scene_frames = detect_scene_changes(video_path, frames_dir, scene_threshold)

    # Merge frames
    print("\nMerging frames...")
    all_frames = merge_frames(baseline_frames, scene_frames)

    # Adjust if we have too many frames
    if len(all_frames) > target_frames:
        # Increase minimum gap between frames
        step = len(all_frames) / target_frames
        all_frames = [all_frames[int(i * step)] for i in range(target_frames)]

    print(f"Total frames: {len(all_frames)}")

    # Build output index
    print("\nMapping frames to transcript...")
    output_frames = []

    for timestamp, filename in all_frames:
        transcript_text, speaker_id, speaker_name = find_transcript_segment(timestamp, segments)

        frame_data = {
            "timestamp": seconds_to_timestamp(timestamp),
            "timestamp_seconds": round(timestamp, 2),
            "screenshot": filename,
            "transcript_segment": transcript_text
        }
        if speaker_id:
            frame_data["speaker_id"] = speaker_id
        if speaker_name:
            frame_data["speaker_name"] = speaker_name

        output_frames.append(frame_data)

    # Get video duration
    duration = get_video_duration(video_path)

    # Create index with enhanced speaker data
    index = {
        "video_file": os.path.basename(video_path),
        "transcript_file": os.path.basename(transcript_path),
        "duration_seconds": round(duration, 2),
        "total_frames": len(output_frames),
        "frame_interval_seconds": frame_interval,
        "scene_detection_threshold": scene_threshold,
        "speaker_analysis": {
            "total_speakers": len(speaker_metrics),
            "total_turns": total_turns,
            "speakers": [
                {
                    "speaker_id": m.speaker_id,
                    "speaker_name": m.speaker_name,
                    "talk_time_seconds": m.talk_time_seconds,
                    "talk_time_pct": m.talk_time_pct,
                    "word_count": m.word_count,
                    "speaking_pace_wpm": m.speaking_pace_wpm,
                    "turn_count": m.turn_count,
                    "avg_turn_length_seconds": m.avg_turn_length_seconds
                }
                for m in speaker_metrics
            ]
        },
        "frames": output_frames
    }

    # Write index.json
    index_path = os.path.join(output_dir, 'index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"{'='*60}")
    print(f"Video duration: {seconds_to_timestamp(duration)}")
    print(f"Frames extracted: {len(output_frames)}")
    print(f"Speakers detected: {len(speaker_metrics)}")
    print(f"Total turns: {total_turns}")
    print(f"Output directory: {output_dir}")
    print(f"Index file: {index_path}")
    print(f"{'='*60}\n")

    return index


def main():
    parser = argparse.ArgumentParser(
        description='Convert video recordings into timestamped screenshots mapped to transcript segments.'
    )
    parser.add_argument('video', help='Path to video file (.mp4 or .mov)')
    parser.add_argument('transcript', help='Path to transcript file (.vtt, .srt, or .txt)')
    parser.add_argument('--output-dir', '-o', help='Output directory (default: ./output/<video_name>)')
    parser.add_argument('--interval', '-i', type=float, default=5.0,
                        help='Baseline frame extraction interval in seconds (default: 5)')
    parser.add_argument('--scene-threshold', '-s', type=float, default=0.3,
                        help='Scene change detection threshold 0-1 (default: 0.3)')
    parser.add_argument('--target-frames', '-t', type=int, default=500,
                        help='Target maximum number of frames (default: 500)')

    args = parser.parse_args()

    # Validate inputs
    if not os.path.exists(args.video):
        print(f"Error: Video file not found: {args.video}")
        sys.exit(1)

    if not os.path.exists(args.transcript):
        print(f"Error: Transcript file not found: {args.transcript}")
        sys.exit(1)

    # Check ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg.")
        sys.exit(1)

    # Process
    process_video(
        args.video,
        args.transcript,
        args.output_dir,
        args.interval,
        args.scene_threshold,
        args.target_frames
    )


if __name__ == '__main__':
    main()
