import queue
import numpy as np
import sounddevice as sd
import json
import time
from faster_whisper import WhisperModel

whisper_model = WhisperModel("large-v3", compute_type="int8")  

audio_queue = queue.Queue()

transcribed_text = []

SAMPLE_RATE = 16000  
BLOCK_SIZE = 4096 
CHANNELS = 1
OUTPUT_JSON = "transcription.json"  
SAVE_INTERVAL = 60  

def get_system_audio_device():
    devices = sd.query_devices()
    print("Available audio devices:")
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")
    
    for device in devices:
        if "Stereo Mix" in device["name"] or "Loopback" in device["name"] or "VB-Audio" in device["name"]:
            return device["index"]
    
    # Fallback to default input device if no system audio device is found
    print("System audio device not found. Using default input device.")
    return sd.default.device[0]

DEVICE_INDEX = get_system_audio_device()

def callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

def save_transcription_to_json(text_list):
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"transcription": text_list}, f, indent=4)
    print(f"Transcription saved to {OUTPUT_JSON}")

def transcribe_audio(update_callback):
    with sd.InputStream(callback=callback, samplerate=SAMPLE_RATE, channels=CHANNELS, 
                        blocksize=BLOCK_SIZE, device=DEVICE_INDEX):
        print("Listening to system audio.")

        start_time = time.time()

        try:
            while True:
                audio_data = []
                while not audio_queue.empty():
                    audio_data.append(audio_queue.get())

                if audio_data:
                    audio_array = np.concatenate(audio_data, axis=0).mean(axis=1).flatten()
                    segments, _ = whisper_model.transcribe(audio_array, language="en")
                    for segment in segments:
                        transcribed_text.append(segment.text)
                        update_callback(f"📝 Transcribed: {segment.text}")

                # Check if it's time to save the transcription
                if time.time() - start_time >= SAVE_INTERVAL:
                    save_transcription_to_json(transcribed_text)
                    start_time = time.time()  # Reset the timer

        except KeyboardInterrupt:
            print("\n⏹️ Stopped listening.")
            save_transcription_to_json(transcribed_text)