#!/bin/bash
#
# process_video.sh - Convert video recordings into timestamped screenshots
#
# Usage:
#   ./process_video.sh <video_file> <transcript_file> [options]
#
# Examples:
#   ./process_video.sh meeting.mp4 transcript.vtt
#   ./process_video.sh call.mov notes.srt --output-dir ./my-output
#   ./process_video.sh demo.mp4 script.txt --interval 3 --scene-threshold 0.4
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 <video_file> <transcript_file> [options]"
    echo ""
    echo "Convert video recordings into timestamped screenshots mapped to transcript segments."
    echo ""
    echo "Arguments:"
    echo "  video_file       Path to video file (.mp4 or .mov)"
    echo "  transcript_file  Path to transcript file (.vtt, .srt, or .txt)"
    echo ""
    echo "Options:"
    echo "  --output-dir, -o DIR     Output directory (default: ./output/<video_name>)"
    echo "  --interval, -i SECONDS   Frame extraction interval (default: 5)"
    echo "  --scene-threshold, -s N  Scene change threshold 0-1 (default: 0.3)"
    echo "  --target-frames, -t N    Target max frames (default: 500)"
    echo "  --help, -h               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 meeting.mp4 transcript.vtt"
    echo "  $0 call.mov notes.srt -o ./output"
    echo "  $0 demo.mp4 script.txt -i 3 -s 0.4 -t 400"
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

# Validate video file
if [[ ! -f "$VIDEO_FILE" ]]; then
    echo -e "${RED}Error: Video file not found: $VIDEO_FILE${NC}"
    exit 1
fi

# Validate transcript file
if [[ ! -f "$TRANSCRIPT_FILE" ]]; then
    echo -e "${RED}Error: Transcript file not found: $TRANSCRIPT_FILE${NC}"
    exit 1
fi

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}Error: ffmpeg is not installed${NC}"
    echo ""
    echo "Install ffmpeg:"
    echo "  macOS:   brew install ffmpeg"
    echo "  Ubuntu:  sudo apt install ffmpeg"
    echo "  Windows: choco install ffmpeg"
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}Starting video processing...${NC}"
echo ""

# Run the Python processor with all arguments
python3 "$SCRIPT_DIR/video_processor.py" "$VIDEO_FILE" "$TRANSCRIPT_FILE" "$@"

exit_code=$?

if [[ $exit_code -eq 0 ]]; then
    echo -e "${GREEN}Video processing completed successfully!${NC}"
else
    echo -e "${RED}Video processing failed with exit code: $exit_code${NC}"
fi

exit $exit_code
