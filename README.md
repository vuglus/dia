# Diamix

A tool to merge diarization files with log files based on timestamps.

## Overview

Diamix takes two files as input:
1. A diarization file (`.dia`) - Contains speaker segments with start time, end time, and speaker ID
2. A log file (`.log`) - Contains dialogue entries with timestamps and speaker names

The tool maps speakers from the diarization file to the log entries based on time overlap and outputs a merged file with the correct speaker names.

## File Formats

### Diarization File (.dia)
```
start_time end_time speaker
0.031 3.119 SPEAKER_02
2.748 3.119 SPEAKER_00
3.119 4.013 SPEAKER_03
```

Times are in seconds.

### Log File (.log)
```
line_number. [speaker] start_time-end_time : text
1. [Спикер 1] 00:00-00:02 : Ну все кроме оперблока его прислали
2. [Спикер 2] 00:00-00:02 : Уже
```

Times are in MM:SS or HH:MM:SS format.

## Usage

```bash
python diamix.py diarization_file.dia log_file.log
```

### Options
- `-o`, `--output`: Output file path (default: stdout)

## Features

1. **Time-based Speaker Mapping**: Matches speakers based on maximum overlap between log entry time ranges and diarization segments
2. **Speaker Consolidation**: Combines consecutive entries from the same speaker
3. **Format Preservation**: Maintains the original log file format with updated speaker names
4. **Sequential Line Numbering**: Outputs entries with sequential line numbers

## Example

Input diarization file:
```
0.031 3.119 SPEAKER_02
2.748 3.119 SPEAKER_00
3.119 4.013 SPEAKER_03
```

Input log file:
```
1. [Спикер 1] 00:00-00:02 : Ну все кроме оперблока его прислали
2. [Спикер 2] 00:00-00:02 : Уже
3. [Спикер 1] 00:02-00:03 : На
```

Output:
```
1. [SPEAKER_02] 00:00-00:02 : Ну все кроме оперблока его прислали Уже
2. [SPEAKER_03] 00:02-00:03 : На
```

## Algorithm

1. Parse both input files
2. For each log entry, find the diarization segment with maximum time overlap
3. Replace speaker names in brackets with diarization speakers
4. Consolidate consecutive entries from the same speaker
5. Output with sequential line numbering