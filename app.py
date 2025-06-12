from flask import Flask
from flask_cors import CORS
from config import UPLOAD_FOLDER, DB_URL
from database import db
from routes.auth_routes import auth_bp
from routes.audio_routes import audio_bp
from routes.user_routes import user_bp
import os
from flask_migrate import Migrate

app = Flask(__name__)
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "https://demo-transcription.iits.ma"}}, 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db.init_app(app)

# Après db.init_app(app)
migrate = Migrate(app, db)
# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(audio_bp)
app.register_blueprint(user_bp)

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flag to track if tables have been created
tables_created = False

@app.before_request
def create_tables():
    global tables_created
    if not tables_created:
        with app.app_context():
            db.create_all()
        tables_created = True

@app.route('/')
def home():
    return "TurboScribe Backend API is running!" # This should return the 'language' field value if it exists

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)