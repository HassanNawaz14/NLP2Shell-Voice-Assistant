import sys
import time
import wave
import array
import math
import pyaudio
import whisper
import warnings
import keyboard

from rich.console import Console
from rich.text import Text

# Suppress whisper warnings
warnings.filterwarnings("ignore")

console = Console()

# Configuration from GEMINI_phase3_4.md
WHISPER_MODEL = "tiny"
SILENCE_THRESHOLD_SECONDS = 2.0
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Load model globally to avoid reloading
_model = None

def _get_model():
    global _model
    if _model is None:
        _model = whisper.load_model(WHISPER_MODEL)
    return _model

def listen() -> str:
    """Record from mic. Stop after 2 seconds of silence. Return transcribed string."""
    p = pyaudio.PyAudio()
    
    try:
        p.get_default_input_device_info()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] No default input device found! {e}")
        return ""

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    with console.status("[bold green]🎤 Listening...[/bold green] [dim](Ctrl+M to switch mode)[/dim]"):
        frames = []
        silent_chunks = 0
        threshold_chunks = int(SILENCE_THRESHOLD_SECONDS * RATE / CHUNK_SIZE)
        RMS_THRESHOLD = 50 

        max_rms = 0
        try:
            while True:
                # Check for instant mode switch (Ctrl+M)
                if keyboard.is_pressed('ctrl+m'):
                    return ""

                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                frames.append(data)
                
                audio_data = array.array('h', data)
                rms = math.sqrt(sum([abs(x)**2 for x in audio_data]) / len(audio_data))
                if rms > max_rms: max_rms = rms
                
                if rms < RMS_THRESHOLD:
                    silent_chunks += 1
                else:
                    silent_chunks = 0
                    
                if silent_chunks > threshold_chunks:
                    break
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    if max_rms < RMS_THRESHOLD:
        return ""

    if len(frames) < 10:
        return ""

    with console.status("[bold blue]Transcribing audio..."):
        temp_filename = "temp_recording.wav"
        wf = wave.open(temp_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        model = _get_model()
        import soundfile as sf
        import numpy as np
        
        audio_data, samplerate = sf.read(temp_filename)
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
            
        result = model.transcribe(audio_data)
    
    return result["text"].strip()

def text_mode() -> str:
    """Read a line from stdin. Return it as string."""
    try:
        return console.input("[bold cyan]⌨  Instruction:[/bold cyan] ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""
