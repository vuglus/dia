#!/bin/bash

# Script to run diarization in the background under WSL
# Usage: ./run_diarization.sh <path-to-mp3>

# Function to convert Windows path to WSL path
convert_path() {
    local input_path="$1"
    
    # Check if it's already a WSL path (starts with /)
    if [[ "$input_path" == /* ]]; then
        echo "$input_path"
        return
    fi
    
    # Convert Windows path (D:\path or D:/path) to WSL path (/mnt/d/path)
    # Handle both forward and backward slashes, and preserve spaces
    echo "$input_path" | sed -E 's/^([A-Za-z]):[\/\\]/\/mnt\/\L\1\//' | sed 's/\\/\//g'
}

# Check if input file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <path-to-mp3>"
    echo "Example: $0 D:/Work/dia/audio/sample.mp3"
    echo "      or $0 /mnt/d/Work/dia/audio/sample.mp3"
    exit 1
fi

# Convert input path if needed
INPUT_FILE=$(convert_path "$1")

# Check if file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File '$INPUT_FILE' not found"
    exit 1
fi

# Run diarization in background
nohup python main.py "$INPUT_FILE" > diarization.log 2>&1 &

# Capture the process ID
PID=$!

echo "Diarization started in background with PID: $PID"
echo "Processing file: $INPUT_FILE"
echo "Logs are being written to diarization.log"
echo "Use 'tail -f diarization.log' to monitor progress"