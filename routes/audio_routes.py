from flask import Blueprint, request, jsonify, send_from_directory
from services.audio_service import save_audio_file, list_user_audios, get_audio_path
from utils.jwt_utils import decode_token
from utils.audio_transcription import transcribe_audio_file
from database import db
from models.audio import AudioFile
import os 
import base64
import tempfile


audio_bp = Blueprint('audio', __name__)


@audio_bp.route('/api/audio/upload', methods=['POST'])
def upload_audio():
    token = request.headers.get('Authorization')
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1] 
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    
    user_id = decode_token(token)
    if not  user_id : 
         return jsonify({'error' : token}), 400


    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    audio_id, error = save_audio_file(file, user_id)  # ➔ PAS de transcription ici
    if error:
        return jsonify({'error': error}), 400

    return jsonify({'message': 'Audio uploaded successfully', 'audio_id': audio_id})


@audio_bp.route('/api/audio/mine', methods=['GET'])
def list_my_audios():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1] 
    user_id = decode_token(token)
    audios = list_user_audios(user_id)

    return jsonify(audios)

@audio_bp.route('/api/audio/<audio_id>', methods=['GET'])
def get_audio(audio_id):
    path = get_audio_path(audio_id)
    if not path:
        return jsonify({'error': 'Audio not found'}), 404
    return send_from_directory(directory=".", path=path, as_attachment=True)


@audio_bp.route('/api/audio/transcribe/<audio_id>', methods=['POST'])
def transcribe_audio(audio_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1] 
    user_id = decode_token(token)
    print(request.json.get("model"))
    # Get the model parameter from the request body
    model = request.json.get("model")
    if not model:
        return jsonify({'error': 'Model name is required'}), 400

    # Validate model name
    valid_models = ["wav2vec", "gemini"]
    if model not in valid_models:
        return jsonify({'error': f"Invalid model name. Choose from {valid_models}."}), 400

    audio = AudioFile.query.get(audio_id)
    if not audio or audio.user_id != user_id:
        return jsonify({'error': 'Audio not found or not yours'}), 404

    try:
        # Call the transcription function with the selected model
        transcription = transcribe_audio_file(audio.filepath, model)

        # Update the database with the transcription
        audio.transcription = transcription
        audio.model_used = model
        db.session.commit()

        return jsonify({'message': 'Transcription done successfully', 'transcription': transcription})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

    # Endpoint to delete audio by ID
@audio_bp.route('/api/audio/delete/<audio_id>', methods=['DELETE'])
def delete_audio(audio_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1] 
    user_id = decode_token(token)

    # Fetch the audio file by ID
    audio = AudioFile.query.get(audio_id)
    if not audio:
        return jsonify({'error': 'Audio file not found'}), 404
    if audio.user_id != user_id:
        return jsonify({'error': 'This audio file does not belong to the current user'}), 403

    try:
        # Delete the audio file from the database
        db.session.delete(audio)
        db.session.commit()

        # Optionally, delete the file from the file system here
        # Example: os.remove(audio.filepath)

        return jsonify({'message': 'Audio deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint to delete all audio for the current user
@audio_bp.route('/api/audio/delete_all', methods=['DELETE'])
def delete_all_audio():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1] 
    user_id = decode_token(token)

    try:
        # Fetch all audio files associated with the current user
        audios = AudioFile.query.filter_by(user_id=user_id).all()
        
        if not audios:
            return jsonify({'error': 'No audio files found for the current user'}), 404

        # Delete all audio files from the database
        for audio in audios:
            db.session.delete(audio)
        
        db.session.commit()

        # Optionally, delete the files from the file system here
        # Example: for audio in audios:
        #               os.remove(audio.filepath)

        return jsonify({'message': 'All audio files deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    



# @audio_bp.route('/api/audio/upload_and_transcribe', methods=['POST'])
# def upload_and_transcribe_audio():
#     token = request.headers.get('Authorization')
#     if token and token.startswith("Bearer "):
#         token = token.split(" ")[1]
#     if not token:
#         return jsonify({'error': 'Missing token'}), 401
    
#     print(token)
#     user_id = decode_token(token)
#     if not user_id:
#         return jsonify({'error': 'Invalid token'}), 400

#     if 'file' not in request.files:
#         return jsonify({'error': 'No file uploaded'}), 400

#     file = request.files['file']
#     print("test")
#     print(file)
#     model = request.json.get("model")
#     print(model)
#     if not model:
#         return jsonify({'error': 'Model name is required'}), 400

#     # Validate model name
#     valid_models = ["wav2vec", "gemini"]

#     if model not in valid_models:
#         return jsonify({'error': f"Invalid model name. Choose from {valid_models}."}), 400

#     # Save audio file
#     audio_id, error = save_audio_file(file, user_id)  # Save the audio file and get its ID
#     if error:
#         return jsonify({'error': error}), 400

#     # Get the file path of the uploaded audio
#     audio = AudioFile.query.get(audio_id)
#     if not audio or audio.user_id != user_id:
#         return jsonify({'error': 'Audio not found or not yours'}), 404

#     try:
#         # Call the transcription function with the selected model
#         transcription = transcribe_audio_file(audio.filepath, model)

#         # Update the database with the transcription
#         audio.transcription = transcription
#         audio.model_used = model
#         db.session.commit()

#         return jsonify({'message': 'Transcription done successfully', 'transcription': transcription})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    

# @audio_bp.route('/api/audio/transcribe_segment', methods=['POST'])
# def transcribe_audio_segment():
#     data = request.json
#     model = data.get('model')
#     segment_index = data.get('segment_index')
#     total_segments = data.get('total_segments')
#     audio_b64 = data.get('audio_base64')

#     if not all([model, segment_index is not None, total_segments, audio_b64]):
#         return jsonify({"error": "Missing parameters"}), 400

#     # Décoder base64 en fichier wav temporaire
#     audio_bytes = base64.b64decode(audio_b64)
#     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
#         tmp_file.write(audio_bytes)
#         temp_wav_path = tmp_file.name

#     try:
#         transcription = transcribe_audio_file(temp_wav_path, model)
#     finally:
#         os.remove(temp_wav_path)

#     progress = int((segment_index + 1) / total_segments * 100)

#     return jsonify({
#         "transcription": transcription,
#         "progress": progress,
#         "segment_index": segment_index
#     })
@audio_bp.route('/api/audio/upload_and_transcribe', methods=['POST'])
def upload_and_transcribe_audio():
    print("hello")

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    # Utilise request.form au lieu de request.json
    model = request.form.get("model")
    language = request.form.get("language", "en")

    if not model:
        return jsonify({'error': 'Model name is required'}), 400

    valid_models = ["wav2vec", "gemini", "whisper"]
    if model not in valid_models:
        return jsonify({'error': f"Invalid model name. Choose from {valid_models}."}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
            file.save(temp.name)
            print(f"Saved temp audio: {temp.name}")

            transcription = transcribe_audio_file(temp.name, model, language)

            # os.remove(temp.name)

            return jsonify({
                'message': 'Transcription done successfully',
                'transcription': transcription,
                'model_used': model,
                'language': language
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
