import os
import warnings
import torchaudio
import torch
import pyannote.audio.core.task 

torch.serialization.add_safe_globals([
    torch.torch_version.TorchVersion,
    pyannote.audio.core.task.Specifications,
    pyannote.audio.core.task.Problem,
    pyannote.audio.core.task.Resolution
])
torch.serialization.weights_only = False

from pyannote.audio import Pipeline

def perform_diarization(file_path, config):
    """
    Perform speaker diarization on an audio file
    
    Args:
        file_path (str): Path to the audio file
        config (dict): Configuration dictionary containing diarization settings
    
    Returns:
        result: Diarization result object
    """
    # Load the diarization pipeline
    pipeline = Pipeline.from_pretrained(
        config['dia']['model'], 
        token=config['dia']["token"]
    )
    pipeline.to(torch.device("cuda"))
    # Load audio with torchaudio to avoid torchcodec issues
    waveform, sample_rate = torchaudio.load(file_path)
    
    # Perform diarization with loaded audio
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = pipeline({"waveform": waveform, "sample_rate": sample_rate})
    
    return result

def save_diarization_result(result, output_path):
    """
    Save diarization result to a .dia file
    
    Args:
        result: Diarization result object
        output_path (str): Path to save the .dia file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for turn, speaker in result.speaker_diarization:
            f.write(f"{turn.start:.3f} {turn.end:.3f} {speaker}\n")