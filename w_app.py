from flask import Flask, request, jsonify
import whisper
import os
import tempfile

app = Flask(__name__)

# Charger le modèle Whisper une seule fois
model = whisper.load_model("large")  # or "base", "small", etc.

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Sauvegarder temporairement le fichier audio
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
            audio_file.save(temp.name)
            print(f"Saved temp audio: {temp.name}")

            # Transcription
            result = model.transcribe(temp.name , language="ar")
            return jsonify({
                'text': result['text']
            })
    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp.name):
            os.remove(temp.name)

if __name__ == '__main__':
    app.run(debug=True)
