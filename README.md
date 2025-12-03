# Diarization Tool

This tool performs speaker diarization on audio files using PyAnnote.

## Prerequisites

- Windows Subsystem for Linux (WSL)
- Python 3.8 or higher
- Required Python packages (install with `pip install -r requiremnets.txt`)

## Usage

### From PowerShell (running in background under WSL)

To run the diarization tool from PowerShell in the background under WSL:

1. Make sure the script is executable (run this from WSL bash):
   ```bash
   chmod +x run_diarization.sh
   ```

2. Run the script with an audio file path using wsl.exe from PowerShell:
   ```powershell
   wsl.exe ./run_diarization.sh "D:\path\to\your\audio.mp3"
   ```

   Example:
   ```powershell
   wsl.exe ./run_diarization.sh "D:\Work\dia\samples\sample.mp3"
   ```

### Direct usage (foreground)

You can also run the tool directly:

```bash
python main.py /path/to/your/audio.mp3
```

## Output

The tool will generate a `.dia` file with the same base name as the input audio file, containing the diarization results in the format:

```
start_time end_time speaker_id
```

Example:
```
0.000 5.231 SPEAKER_00
5.231 12.456 SPEAKER_01
```

## Monitoring Background Process

When running in background mode, you can monitor the progress with:

```bash
tail -f diarization.log
```

To check if the process is still running:
```bash
ps aux | grep python