import os
import uuid
from models.audio import AudioFile
from database import db
from config import UPLOAD_FOLDER
from utils.audio_transcription import transcribe_audio_file

def save_audio_file(file, user_id):
    if not file:
        return None, 'No file provided'
    if not user_id:
        return None , 'User Id'

    filename = str(uuid.uuid4()) + '_' + file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    print(user_id)

    try:
        file.save(filepath)
    except Exception as e:
        return None, str(e)

    new_audio = AudioFile(
        user_id=user_id,
        filename=file.filename,
        filepath=filepath,
        transcription=None,  # Aucune transcription encore
        model_used='SynergyIA'      # Aucun modèle utilisé encore
    )
    db.session.add(new_audio)
    db.session.commit()

    return new_audio.id, None


def list_user_audios(user_id):
    audios = AudioFile.query.filter_by(user_id=user_id).all()
    return [{'id': a.id, 'filename': a.filename, 'transcription': a.transcription , 'language':a.language} for a in audios]

def get_audio_path(audio_id):
    audio = AudioFile.query.get(audio_id)
    if not audio:
        return None
    return audio.filepath
