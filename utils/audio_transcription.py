import librosa
import soundfile as sf
from pydub import AudioSegment
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2CTCTokenizer, Wav2Vec2ForCTC
import os
import numpy as np
import whisper

whisper_model = whisper.load_model("large")

model_name = "boumehdi/wav2vec2-large-xlsr-moroccan-darija"
model = Wav2Vec2ForCTC.from_pretrained(model_name)
processor = Wav2Vec2Processor.from_pretrained(model_name)
tokenizer = Wav2Vec2CTCTokenizer.from_pretrained(model_name)

def convert_audio_to_wav(file_path):
    audio = AudioSegment.from_file(file_path)
    wav_path = file_path.rsplit('.', 1)[0] + ".wav"
    audio.export(wav_path, format="wav")
    return wav_path

def load_audio(file_path):
    if not file_path.endswith('.wav'):
        file_path = convert_audio_to_wav(file_path)
    audio, _ = librosa.load(file_path, sr=16000)
    return audio

def transcribe_audio_with_wav2vec2(file_path):
    audio = load_audio(file_path)
    audio_length = len(audio) / 16000  # audio length in seconds

    # If audio is longer than 30 seconds, split it into smaller segments
    segment_length = 30  # segment length in seconds
    transcriptions = []

    if audio_length > segment_length:
        # Split the audio into chunks of 30 seconds
        num_segments = int(np.ceil(audio_length / segment_length))

        for i in range(num_segments):
            start_sample = i * segment_length * 16000
            end_sample = min((i + 1) * segment_length * 16000, len(audio))
            audio_segment = audio[start_sample:end_sample]

            # Process the segment and get transcription
            inputs = processor(audio_segment, return_tensors="pt", padding=True)
            input_features = inputs['input_values']

            if torch.cuda.is_available():
                model.to("cuda")
                input_features = input_features.to("cuda")

            with torch.no_grad():
                logits = model(input_features).logits

            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = tokenizer.batch_decode(predicted_ids, skip_special_tokens=True)

            transcriptions.append(transcription[0])

        # Combine all segment transcriptions into one final transcription
        final_transcription = " ".join(transcriptions)

    else:
        # If audio is less than or equal to 30 seconds, process it directly
        inputs = processor(audio, return_tensors="pt", padding=True)
        input_features = inputs['input_values']

        if torch.cuda.is_available():
            model.to("cuda")
            input_features = input_features.to("cuda")

        with torch.no_grad():
            logits = model(input_features).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = tokenizer.batch_decode(predicted_ids, skip_special_tokens=True)

        final_transcription = transcription[0]

    return final_transcription


def transcribe_audio_file(file_path, model, language):
    # Handle transcription based on model selection
    if model == "whisper":
        result = whisper_model.transcribe(file_path, language=language)
        return result["text"]
    elif model == "gemini":
        return transcribe_audio_with_gemini(file_path)
    elif model == "wav2vec":
        return transcribe_audio_with_wav2vec2(file_path)
    else:
        raise ValueError("Unsupported model")
    


import base64
from google import genai

# Define your API Key and Client
API_KEY = "AIzaSyAiDMkcsELd162osJWzrDza3JmORQutrI4"
client = genai.Client(api_key=API_KEY)

# Function to convert the audio file to base64
def file_to_base64(file_path):
    """ Convert the audio file to base64 encoding. """
    with open(file_path, 'rb') as audio_file:
        return base64.b64encode(audio_file.read()).decode('utf-8')

# Function to transcribe audio with Gemini API using genai Client
def transcribe_audio_with_gemini(file_path):
    try:
        # Step 1: Convert audio file to base64
        base64_audio = file_to_base64(file_path)

        # Step 2: Prepare the request content
        contents = [
            {
                "parts": [
                    {
                        "text": "Transcribe this audio file."
                    },
                    {
                        "inline_data": {
                            "mime_type": "audio/wav",  # You can adjust this based on your audio file type
                            "data": base64_audio  # The base64 encoded audio data
                        }
                    }
                ]
            }
        ]

        # Step 3: Send the request to the Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # You can use the correct model based on your requirements
            contents=contents
        )

        # Step 4: Check if the transcription was successful and print the result
        if response.text:
            print("Transcription Result:", response.text)
            return response.text
        else:
            print("No transcription result found.")
            return None

    except Exception as e:
        print(f"Error during transcription: {e}")
        return None