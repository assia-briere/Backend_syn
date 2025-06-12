from database import db
import uuid
from datetime import datetime

class AudioFile(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    transcription = db.Column(db.Text, nullable=True)
    model_used = db.Column(db.String(50))  # 🔥 nouvelle colonne ici
    language = db.Column(db.String(50), nullable=True)  # Add the new 'language' column here
 # Adding the 'language' column

