#!/bin/bash
#
# review_call.sh - Comprehensive call review for sales and client calls
#
# Orchestrates video frame extraction and transcript analysis to produce
# a structured call review with speaker metrics, pattern detection, and
# visual analysis preparation.
#
# Usage:
#   ./review_call.sh <video_file> <transcript_file> [options]
#
# Examples:
#   ./review_call.sh meeting.mp4 transcript.vtt
#   ./review_call.sh call.mov notes.srt --call-type demo
#   ./review_call.sh acme_discovery.mp4 transcript.vtt --call-type discovery -o ./reviews
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 <video_file> <transcript_file> [options]"
    echo ""
    echo "Comprehensive call review for sales and client calls."
    echo ""
    echo "Arguments:"
    echo "  video_file       Path to video file (.mp4 or .mov)"
    echo "  transcript_file  Path to transcript file (.vtt, .srt, or .txt)"
    echo ""
    echo "Options:"
    echo "  --call-type, -c TYPE   Type of call: discovery, demo, checkin (default: discovery)"
    echo "  --output-dir, -o DIR   Output directory (default: ./output/<video_name>)"
    echo "  --interval, -i SECS    Frame extraction interval (default: 5)"
    echo "  --scene-threshold, -s  Scene change threshold 0-1 (default: 0.3)"
    echo "  --target-frames, -t N  Target max frames (default: 500)"
    echo "  --skip-video           Skip video processing (use existing frames)"
    echo "  --help, -h             Show this help message"
    echo ""
    echo "Output:"
    echo "  output/<video_name>/"
    echo "    frames/              Extracted video frames"
    echo "    index.json           Frame-to-transcript mapping with speaker metrics"
    echo "    call_review.json     Comprehensive call analysis"
    echo ""
    echo "Examples:"
    echo "  $0 acme_discovery.mp4 transcript.vtt --call-type discovery"
    echo "  $0 demo_recording.mov demo.srt -c demo -o ./demo_review"
    echo "  $0 checkin.mp4 notes.txt --call-type checkin --skip-video"
}

# Check for help flag first
for arg in "$@"; do
    if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
        print_usage
        exit 0
    fi
done

# Check minimum arguments
if [[ $# -lt 2 ]]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    print_usage
    exit 1
fi

VIDEO_FILE="$1"
TRANSCRIPT_FILE="$2"
shift 2

# Default options
CALL_TYPE="discovery"
OUTPUT_DIR=""
INTERVAL="5"
SCENE_THRESHOLD="0.3"
TARGET_FRAMES="500"
SKIP_VIDEO=false

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --call-type|-c)
            CALL_TYPE="$2"
            shift 2
            ;;
        --output-dir|-o)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --interval|-i)
            INTERVAL="$2"
            shift 2
            ;;
        --scene-threshold|-s)
            SCENE_THRESHOLD="$2"
            shift 2
            ;;
        --target-frames|-t)
            TARGET_FRAMES="$2"
            shift 2
            ;;
        --skip-video)
            SKIP_VIDEO=true
            shift
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

# Validate call type
if [[ ! "$CALL_TYPE" =~ ^(discovery|demo|checkin)$ ]]; then
    echo -e "${RED}Error: Invalid call type: $CALL_TYPE${NC}"
    echo "Valid types: discovery, demo, checkin"
    exit 1
fi

# Validate video file (unless skipping)
if [[ "$SKIP_VIDEO" == false && ! -f "$VIDEO_FILE" ]]; then
    echo -e "${RED}Error: Video file not found: $VIDEO_FILE${NC}"
    exit 1
fi

# Validate transcript file
if [[ ! -f "$TRANSCRIPT_FILE" ]]; then
    echo -e "${RED}Error: Transcript file not found: $TRANSCRIPT_FILE${NC}"
    exit 1
fi

# Check for ffmpeg (unless skipping video)
if [[ "$SKIP_VIDEO" == false ]]; then
    if ! command -v ffmpeg &> /dev/null; then
        echo -e "${RED}Error: ffmpeg is not installed${NC}"
        echo ""
        echo "Install ffmpeg:"
        echo "  macOS:   brew install ffmpeg"
        echo "  Ubuntu:  sudo apt install ffmpeg"
        echo "  Windows: choco install ffmpeg"
        exit 1
    fi
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Determine output directory
if [[ -z "$OUTPUT_DIR" ]]; then
    VIDEO_NAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
    OUTPUT_DIR="$SCRIPT_DIR/output/$VIDEO_NAME"
fi

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}           Call Review Skill                                ${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "Video:      ${GREEN}$VIDEO_FILE${NC}"
echo -e "Transcript: ${GREEN}$TRANSCRIPT_FILE${NC}"
echo -e "Call Type:  ${GREEN}$CALL_TYPE${NC}"
echo -e "Output:     ${GREEN}$OUTPUT_DIR${NC}"
echo ""

# Step 1: Process video (unless skipping)
if [[ "$SKIP_VIDEO" == false ]]; then
    echo -e "${YELLOW}Step 1/2: Processing video and extracting frames...${NC}"
    echo ""

    python3 "$SCRIPT_DIR/video_processor.py" \
        "$VIDEO_FILE" \
        "$TRANSCRIPT_FILE" \
        --output-dir "$OUTPUT_DIR" \
        --interval "$INTERVAL" \
        --scene-threshold "$SCENE_THRESHOLD" \
        --target-frames "$TARGET_FRAMES"

    if [[ $? -ne 0 ]]; then
        echo -e "${RED}Error: Video processing failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Step 1/2: Skipping video processing (using existing frames)${NC}"

    # Check that index.json exists
    if [[ ! -f "$OUTPUT_DIR/index.json" ]]; then
        echo -e "${RED}Error: index.json not found in $OUTPUT_DIR${NC}"
        echo "Run without --skip-video first, or specify correct output directory."
        exit 1
    fi
fi

# Step 2: Analyze call
echo ""
echo -e "${YELLOW}Step 2/2: Analyzing call patterns and generating review...${NC}"
echo ""

python3 "$SCRIPT_DIR/call_analyzer.py" \
    "$OUTPUT_DIR/index.json" \
    --call-type "$CALL_TYPE" \
    --output-dir "$OUTPUT_DIR"

if [[ $? -ne 0 ]]; then
    echo -e "${RED}Error: Call analysis failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}           Call Review Complete!                            ${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo "Output files:"
echo "  - $OUTPUT_DIR/frames/           (extracted frames)"
echo "  - $OUTPUT_DIR/index.json        (frame mapping + speaker metrics)"
echo "  - $OUTPUT_DIR/call_review.json  (comprehensive analysis)"
echo ""
echo "Next steps:"
echo "  1. Open Claude Code in the output directory"
echo "  2. Load call_review.json and frames for analysis"
echo "  3. Use prompts from prompts/ directory for specific analysis"
echo ""
echo "Example Claude Code analysis:"
echo "  Read output/$VIDEO_NAME/call_review.json and review the frames."
echo "  Analyze this $CALL_TYPE call for:"
echo "  1. Pain points uncovered and their severity"
echo "  2. Visual engagement cues in the frames"
echo "  3. How objections were handled"
echo "  4. Recommended next steps"
echo ""
echo -e "${GREEN}============================================================${NC}"

exit 0
