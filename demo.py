import asyncio
import pyaudio
from uuid import uuid4
import boto3
import wave

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5  # Adjust the duration as needed
OUTPUT_FILE = f"audios/{uuid4()}.wav"


# Specify your access key and secret key
access_key = 'access key ID'
secret_key = 'Secret key ID'

# Create an S3 client with your credentials
s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

bucket_name = 'enter bucket name farhan'
local_file_path = OUTPUT_FILE

comprehend = boto3.client('comprehend')

"""
Here's an example of a custom event handler you can extend to
process the returned transcription results as needed. This
handler will simply print the text out to your interpreter.
"""
class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                print(alt.transcript)
                # response = comprehend.detect_sentiment(Text=alt.transcript, LanguageCode='en')
                # sentiment = response['Sentiment']
                # score = response['SentimentScore']
                # print(f"{alt.transcript} {sentiment} {score}")

async def basic_transcribe():
    # Set up our client with your chosen Region
    client = TranscribeStreamingClient(region="us-east-1")

    # Start transcription to generate async stream
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=44100,
        media_encoding="pcm",
    )

    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    async def write_chunks():
        # Initialize PyAudio
        audio = pyaudio.PyAudio()

        # Open the microphone stream
        audio_stream = audio.open(format=pyaudio.paInt16,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        print("Transcribing...")
        frames = []

        # Stream audio data to transcription client in chunks
        try:
            for i in range(int(RATE / CHUNK * RECORD_SECONDS)): # Take Audio of RECORD_SECONDS number of seconds
            # while True: # Take Audio until cancelled
                data = audio_stream.read(CHUNK)
                await stream.input_stream.send_audio_event(audio_chunk=data)
                frames.append(data)

        except asyncio.CancelledError:
            pass
        finally:
            # Clean up the stream and PyAudio
            audio_stream.stop_stream()
            audio_stream.close()
            audio.terminate()
            wave_file = wave.open(OUTPUT_FILE, 'wb')
            wave_file.setnchannels(CHANNELS)
            wave_file.setsampwidth(audio.get_sample_size(FORMAT))
            wave_file.setframerate(RATE)
            wave_file.writeframes(b''.join(frames))
            wave_file.close()
            s3.upload_file(local_file_path, bucket_name, OUTPUT_FILE)

    await asyncio.gather(write_chunks(), handler.handle_events())

# Run the transcription
loop = asyncio.get_event_loop()
loop.run_until_complete(basic_transcribe())
loop.close()
