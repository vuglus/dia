#!/usr/bin/env python3
"""
Diamix - A tool to merge diarization files with log files based on timestamps
"""

import re
import argparse
from collections import defaultdict
from datetime import datetime, timedelta


def seconds_to_timestamp(seconds):
    """
    Convert seconds to timestamp string (HH:MM:SS.mmm)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def timestamp_to_seconds(timestamp_str):
    """
    Convert timestamp string to seconds
    Format: HH:MM:SS or MM:SS
    """
    parts = timestamp_str.split(':')
    if len(parts) == 3:
        # HH:MM:SS
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    elif len(parts) == 2:
        # MM:SS
        minutes, seconds = parts
        return int(minutes) * 60 + int(seconds)
    else:
        # SS
        return int(parts[0])


def parse_dia_file(dia_path):
    """
    Parse diarization file and return speaker segments
    Format: start_time end_time speaker
    Times are in seconds
    """
    segments = []
    
    try:
        with open(dia_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Match pattern like: 0.031 3.119 SPEAKER_02
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        start_time = float(parts[0])
                        end_time = float(parts[1])
                        speaker = ' '.join(parts[2:])  # In case speaker name has spaces
                        
                        segments.append({
                            'start': start_time,
                            'end': end_time,
                            'speaker': speaker,
                            'line_num': line_num
                        })
                    except ValueError as e:
                        print(f"Warning: Could not parse times on line {line_num}: {e}")
                else:
                    print(f"Warning: Could not parse line {line_num}: {line}")
    
    except FileNotFoundError:
        print(f"Error: File {dia_path} not found")
        return []
    except Exception as e:
        print(f"Error reading {dia_path}: {e}")
        return []
    
    # Sort segments by start time
    segments.sort(key=lambda x: x['start'])
    return segments


def parse_log_file(log_path):
    """
    Parse log file and return dialogue entries
    Expected format: line_number. [speaker] start_time-end_time : text
    """
    entries = []
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Match pattern like: 1. [Спикер 1] 00:00-00:02 : Ну все кроме оперблока его прислали
                match = re.match(r'\d+\.\s*\[([^\]]+)\]\s*([^-]+)-([^\s]+)\s*:\s*(.*)', line)
                if match:
                    log_speaker, start_time_str, end_time_str, text = match.groups()
                    try:
                        start_time = timestamp_to_seconds(start_time_str.strip())
                        end_time = timestamp_to_seconds(end_time_str.strip())
                        entries.append({
                            'start_time': start_time,
                            'end_time': end_time,
                            'log_speaker': log_speaker.strip(),
                            'text': text.strip(),
                            'original_line': line,
                            'original_start_time': start_time_str.strip(),
                            'original_end_time': end_time_str.strip()
                        })
                    except ValueError as e:
                        print(f"Warning: Could not parse timestamp on line {line_num}: {e}")
                else:
                    print(f"Warning: Could not parse line {line_num}: {line}")
    
    except FileNotFoundError:
        print(f"Error: File {log_path} not found")
        return []
    except Exception as e:
        print(f"Error reading {log_path}: {e}")
        return []
    
    # Sort entries by start time
    entries.sort(key=lambda x: x['start_time'])
    return entries


def get_dia_speaker(dia_segments, start_time, end_time):
    """
    Get the speaker from diarization segments that best matches the time range
    Returns the speaker with the maximum overlap with the given time range
    """
    if not dia_segments:
        return "UNKNOWN"
    
    max_overlap = 0
    best_speaker = "UNKNOWN"
    
    for segment in dia_segments:
        # Calculate overlap between segments
        overlap_start = max(start_time, segment['start'])
        overlap_end = min(end_time, segment['end'])
        
        if overlap_start < overlap_end:  # There is an overlap
            overlap_duration = overlap_end - overlap_start
            if overlap_duration > max_overlap:
                max_overlap = overlap_duration
                best_speaker = segment['speaker']
    
    return best_speaker


def merge_files(dia_segments, log_entries):
    """
    Merge diarization segments with log entries based on timestamps
    """
    if not dia_segments or not log_entries:
        return []
    
    # Create a mapping from time ranges to speakers
    merged_entries = []
    
    for entry in log_entries:
        start_time = entry['start_time']
        end_time = entry['end_time']
        log_speaker = entry['log_speaker']
        text = entry['text']
        original_line = entry['original_line']
        original_start_time = entry['original_start_time']
        original_end_time = entry['original_end_time']
        
        # Find the corresponding speaker in diarization segments using overlap
        dia_speaker = get_dia_speaker(dia_segments, start_time, end_time)
        
        merged_entries.append({
            'start_time': start_time,
            'end_time': end_time,
            'log_speaker': log_speaker,
            'dia_speaker': dia_speaker,
            'text': text,
            'original_line': original_line,
            'original_start_time': original_start_time,
            'original_end_time': original_end_time
        })
    
    return merged_entries


def consolidate_speakers(merged_entries):
    """
    Consolidate consecutive entries from the same speaker
    """
    if not merged_entries:
        return []
    
    consolidated = []
    current_entry = merged_entries[0].copy()
    
    for i in range(1, len(merged_entries)):
        next_entry = merged_entries[i]
        
        # If same diarization speaker and close in time, consolidate
        time_diff = abs(next_entry['start_time'] - current_entry['end_time'])
        if (next_entry['dia_speaker'] == current_entry['dia_speaker'] and 
            time_diff <= 5):  # Within 5 seconds
            # Update end time to the later of the two
            current_entry['end_time'] = max(current_entry['end_time'], next_entry['end_time'])
            # Append text to current entry
            current_entry['text'] += " " + next_entry['text']
        else:
            # Save current entry and start new one
            consolidated.append(current_entry)
            current_entry = next_entry.copy()
    
    # Don't forget the last entry
    consolidated.append(current_entry)
    
    return consolidated


def output_merged(merged_entries, output_path=None):
    """
    Output merged entries to file or stdout, replacing speakers in brackets
    """
    lines = []
    for i, entry in enumerate(merged_entries):
        # Replace the speaker in brackets with the diarization speaker
        if entry['dia_speaker'] != "UNKNOWN":
            # Create new line with sequential numbering
            new_line = f"{i+1}. [{entry['dia_speaker']}] {entry['original_start_time']}-{entry['original_end_time']} : {entry['text']}"
            lines.append(new_line)
        else:
            # Keep original line if speaker is unknown but update line number
            updated_line = re.sub(r'^\d+\.', f'{i+1}.', entry['original_line'])
            lines.append(updated_line)
    
    output_text = "\n".join(lines)
    
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"Merged output written to {output_path}")
        except Exception as e:
            print(f"Error writing to {output_path}: {e}")
            print("Output to console instead:")
            print(output_text)
    else:
        print(output_text)


def main():
    parser = argparse.ArgumentParser(description="Merge diarization and log files")
    parser.add_argument("dia_file", help="Path to diarization file")
    parser.add_argument("log_file", help="Path to log file")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    
    args = parser.parse_args()
    
    print(f"Parsing diarization file: {args.dia_file}")
    dia_segments = parse_dia_file(args.dia_file)
    print(f"Found {len(dia_segments)} segments")
    
    print(f"Parsing log file: {args.log_file}")
    log_entries = parse_log_file(args.log_file)
    print(f"Found {len(log_entries)} entries")
    
    print("Merging files...")
    merged_entries = merge_files(dia_segments, log_entries)
    print(f"Merged {len(merged_entries)} entries")
    
    print("Consolidating speakers...")
    consolidated = consolidate_speakers(merged_entries)
    print(f"Consolidated to {len(consolidated)} entries")
    
    print("Outputting result...")
    output_merged(consolidated, args.output)


if __name__ == "__main__":
    main()