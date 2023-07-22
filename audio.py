import pyaudio
import wave

# Constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5  # Adjust the duration as needed
OUTPUT_FILE = "audio.wav"

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open the microphone stream
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

print("Recording started.")

# Start recording
frames = []
for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Recording finished.")

# Stop the stream
stream.stop_stream()
stream.close()
audio.terminate()

# Save the recorded audio to a file
wave_file = wave.open(OUTPUT_FILE, 'wb')
wave_file.setnchannels(CHANNELS)
wave_file.setsampwidth(audio.get_sample_size(FORMAT))
wave_file.setframerate(RATE)
wave_file.writeframes(b''.join(frames))
wave_file.close()

print(f"Audio saved to {OUTPUT_FILE}.")
