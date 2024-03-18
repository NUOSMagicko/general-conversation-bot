import os
from dotenv import load_dotenv
from openai import OpenAI
import pyaudio
import wave
import keyboard
import time

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
OUTPUT_FILENAME = "recordedFile.wav"

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT , channels=CHANNELS , rate=RATE, input=True, frames_per_buffer=CHUNK)

frames = []
print("Press space to start recording.")
keyboard.wait("space")
print("Recording ... Press SPACE to stop.")
time.sleep(0.2)

while True:
    try:
        data = stream.read(CHUNK)
        frames.append(data)
    except KeyboardInterrupt:
        break
    if keyboard.is_pressed('space'):
        print("Stopping recording after a brief delay ...")
        time.sleep(0.2)
        break

stream.stop_stream()
stream.close()
audio.terminate()

waveFile = wave.open(OUTPUT_FILENAME , "wb")
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Construct the absolute path to the MP3 file
mp3_file_path = os.path.join(os.path.dirname(__file__), "recordedFile.wav")

# Open the MP3 file in binary mode
with open(mp3_file_path, "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )

# Print the transcription text
print( "You : " + transcription.text)

def get_GPT305_Response(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {
                "role" : "user",
                "content" : prompt,
            }
        ],
        response_format={"type" : "text"},
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

gpt_response_text = get_GPT305_Response(transcription.text)
print("GPT 3.5 Turbo : " + gpt_response_text)
