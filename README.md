# Sales Video Review

A picture says a thousand words. A video—a million.

Yet in the world of notetakers and call analytics, we've been stuck with text analysis. Transcripts. Summaries. Keywords. Meanwhile, the richest data—facial expressions, body language, visual reactions—gets thrown away.

**That changes. Now.**

Capture emotions, responses, and contextually analyze your video calls. This tool combines visual frame analysis with transcript pattern detection to surface insights that text alone can never reveal.

## What It Does

- **Extracts video frames** at key moments (regular intervals + scene changes)
- **Detects speakers** from transcript labels and calculates talk-time metrics
- **Identifies patterns** in conversation: pain points, objections, buying signals, action items
- **Classifies questions** as open discovery vs closed confirmation
- **Generates health indicators** based on call type
- **Prepares data** for visual engagement analysis in Claude Code

## Quick Start

```bash
./review_call.sh meeting.mp4 transcript.vtt --call-type discovery
```

This creates:
```
output/meeting/
├── frames/              # Extracted video frames
│   ├── frame_0001.jpg
│   ├── scene_0001.jpg
│   └── ...
├── index.json           # Frame mapping + speaker metrics
└── call_review.json     # Comprehensive call analysis
```

Then analyze in Claude Code:
```
Read output/meeting/call_review.json and the frames.
Analyze this discovery call for pain points and visual engagement cues.
```

## Requirements

- **ffmpeg**: Video processing
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: `choco install ffmpeg`
- **Python 3.6+**: Standard library only

## Usage

### Basic Usage

```bash
./review_call.sh <video_file> <transcript_file> [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--call-type`, `-c` | `discovery` | Type: `discovery`, `demo`, `checkin` |
| `--output-dir`, `-o` | `./output/<video_name>` | Output directory |
| `--interval`, `-i` | `5` | Seconds between baseline frames |
| `--scene-threshold`, `-s` | `0.3` | Scene detection sensitivity (0-1) |
| `--target-frames`, `-t` | `500` | Maximum frames to extract |
| `--skip-video` | - | Skip video processing, use existing frames |

### Examples

```bash
# Discovery call analysis
./review_call.sh acme_discovery.mp4 transcript.vtt --call-type discovery

# Product demo review
./review_call.sh demo_recording.mov demo.srt -c demo

# Client health check
./review_call.sh quarterly_checkin.mp4 notes.txt -c checkin

# Re-analyze with different call type (skip video processing)
./review_call.sh call.mp4 transcript.vtt -c demo --skip-video -o ./output/call
```

## Supported Formats

### Video
- `.mp4`, `.mov`, and any format supported by ffmpeg

### Transcript
- **VTT** (WebVTT) - Zoom, Grain, most platforms
- **SRT** - Standard subtitle format
- **Plain text** with timestamps

Speaker detection works with:
- VTT voice tags: `<v John Smith>Hello`
- Colon format: `John Smith: Hello`
- Various timestamp patterns

## Output Files

### index.json

Frame-to-transcript mapping with speaker metrics:

```json
{
  "video_file": "meeting.mp4",
  "transcript_file": "transcript.vtt",
  "duration_seconds": 1847,
  "speaker_analysis": {
    "total_speakers": 2,
    "total_turns": 47,
    "speakers": [
      {
        "speaker_id": "speaker_1",
        "speaker_name": "John Smith",
        "talk_time_seconds": 892.5,
        "talk_time_pct": 48.3,
        "word_count": 2340,
        "speaking_pace_wpm": 157.3,
        "turn_count": 24,
        "avg_turn_length_seconds": 37.2
      }
    ]
  },
  "frames": [
    {
      "timestamp": "00:01:15",
      "timestamp_seconds": 75.0,
      "screenshot": "frame_0015.jpg",
      "transcript_segment": "Our main challenge is compliance tracking...",
      "speaker_id": "speaker_2",
      "speaker_name": "Jane Prospect"
    }
  ]
}
```

### call_review.json

Comprehensive analysis output:

```json
{
  "call_metadata": {
    "video_file": "meeting.mp4",
    "duration_seconds": 1847,
    "call_type": "discovery"
  },
  "speaker_analysis": { ... },
  "transcript_analysis": {
    "questions_asked": {
      "total": 15,
      "by_type": {
        "open_discovery": 8,
        "closed_confirmation": 5,
        "clarifying": 2
      },
      "details": [ ... ]
    },
    "pain_points_identified": {
      "total": 4,
      "high_confidence": 2,
      "details": [
        {
          "pattern_type": "pain_point",
          "text": "Our biggest challenge is tracking compliance...",
          "timestamp": "00:03:24",
          "speaker_name": "Jane Prospect",
          "confidence": "high",
          "matched_phrase": "our biggest challenge"
        }
      ]
    },
    "objections_detected": { ... },
    "buying_signals": { ... },
    "action_items": { ... }
  },
  "visual_analysis": {
    "total_frames": 432,
    "engagement_timeline": [],
    "notable_reactions": []
  },
  "summary": {
    "key_metrics": {
      "duration_minutes": 30.8,
      "questions_asked": 15,
      "pain_points_found": 4,
      "objections_raised": 2,
      "buying_signals_detected": 3
    },
    "call_health_indicators": {
      "talk_ratio": {
        "status": "good",
        "message": "Good balance with top speaker at 52%"
      },
      "question_quality": {
        "status": "good",
        "message": "53% open-ended, 47% closed questions"
      }
    }
  }
}
```

## Pattern Detection

### Pain Points
Detects phrases like:
- "our biggest challenge", "we struggle with"
- "frustrating", "takes too long", "inefficient"
- "manual process", "outdated", "workaround"

### Objections
Detects phrases like:
- "we've tried before", "budget", "not sure if"
- "need to think about it", "talk to my manager"
- "already have", "too complex", "not a priority"

### Buying Signals
Detects phrases like:
- "what's the next step", "how quickly"
- "what's the pricing", "implementation"
- "pilot", "proof of concept"

### Action Items
Detects phrases like:
- "I'll send", "let's schedule"
- "by Friday", "follow up"
- "put together", "introduce you to"

## Claude Code Integration

### Basic Analysis

```
Read output/acme_discovery/call_review.json

Analyze this discovery call:
1. What pain points were uncovered?
2. How were objections handled?
3. What are the recommended next steps?
```

### Visual Analysis

```
Read output/acme_discovery/call_review.json
Read output/acme_discovery/frames/frame_0045.jpg

Look at the frame from timestamp 03:45 when the pain point was discussed.
What does the prospect's body language indicate about their engagement?
```

### Use Prompt Templates

See the `prompts/` directory for detailed analysis templates:

- **prompts/discovery_call.md** - Discovery call qualification and analysis
- **prompts/demo_review.md** - Product demo engagement analysis
- **prompts/checkin_health.md** - Client health and expansion signals
- **prompts/visual_cues.md** - Guide for analyzing visual indicators
- **prompts/disc_analysis.md** - DISC personality profile analysis and coaching

## Call Type Guidelines

### Discovery Calls (`--call-type discovery`)
Health indicators optimized for:
- Prospect should talk 60%+ of time
- Open-ended questions preferred
- Pain point discovery expected
- Clear next steps important

### Product Demos (`--call-type demo`)
Health indicators optimized for:
- More rep talk time expected
- Feature engagement tracking
- Objection identification
- Buying signal detection

### Client Check-ins (`--call-type checkin`)
Health indicators optimized for:
- Satisfaction signals
- Expansion opportunities
- Risk indicators
- Relationship health

## File Structure

```
video-to-frames/
├── review_call.sh         # Main entry point
├── video_processor.py     # Frame extraction + speaker metrics
├── call_analyzer.py       # Pattern detection + analysis
├── process_video.sh       # Legacy video-only processing
├── README.md              # This documentation
├── prompts/               # Claude analysis prompt templates
│   ├── discovery_call.md
│   ├── demo_review.md
│   ├── checkin_health.md
│   ├── visual_cues.md
│   └── disc_analysis.md
├── samples/               # Sample transcript files
└── output/                # Default output location
```

## Python API

### Video Processing

```python
from video_processor import process_video, parse_transcript, compute_speaker_metrics

# Process video with speaker detection
index = process_video(
    video_path='meeting.mp4',
    transcript_path='transcript.vtt',
    output_dir='./output/meeting'
)

# Parse transcript separately
segments = parse_transcript('transcript.vtt')

# Compute speaker metrics
metrics, speaker_segments, total_turns = compute_speaker_metrics(segments)
```

### Call Analysis

```python
from call_analyzer import generate_call_review
import json

# Load index
with open('output/meeting/index.json') as f:
    index_data = json.load(f)

# Generate call review
review = generate_call_review(index_data, call_type='discovery')

# Access results
print(f"Pain points: {review['summary']['key_metrics']['pain_points_found']}")
print(f"Health: {review['summary']['call_health_indicators']}")
```

## Troubleshooting

### "ffmpeg not found"
Install ffmpeg for your platform (see Requirements).

### Speaker detection not working
Ensure transcript has speaker labels:
- VTT: `<v Speaker Name>text`
- SRT/TXT: `Speaker Name: text`

If no labels exist, all segments are attributed to "unknown".

### Low frame quality
Modify `-q:v` value in video_processor.py (lower = higher quality, 1-31).

### Too many/few frames
Adjust `--interval` and `--scene-threshold`:
- Lower interval = more baseline frames
- Lower threshold = more scene change detection

### Memory issues with long videos
For 2+ hour videos:
- Increase interval to 10-15 seconds
- Reduce target frames to 300
- Process in segments

## Example Workflow

1. **Process the call**
   ```bash
   ./review_call.sh acme_discovery.mp4 transcript.vtt -c discovery
   ```

2. **Open Claude Code**
   ```bash
   cd output/acme_discovery
   claude
   ```

3. **Load and analyze**
   ```
   Read call_review.json

   Based on this discovery call analysis:
   1. Summarize the top 3 pain points by severity
   2. What buying signals indicate deal momentum?
   3. How should I position the follow-up email?
   ```

4. **Visual review**
   ```
   Read frames/frame_0089.jpg

   This frame is from 07:25 when the main objection was raised.
   What does the prospect's body language tell us?
   ```

5. **Generate follow-up**
   ```
   Based on the call_review.json analysis and frames I've shown you,
   draft a follow-up email that:
   - Acknowledges their main pain point
   - Addresses the budget objection
   - Proposes clear next steps
   ```
