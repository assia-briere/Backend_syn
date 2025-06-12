from models.user import User
from database import db
from utils.hashing import hash_password, verify_password
from utils.jwt_utils import generate_token

def register_user(username, email, password):
    if User.query.filter_by(email=email).first():
        return None, 'Email already exists'
    
    new_user = User(
        username=username,
        email=email,
        password_hash=hash_password(password)
    )
    db.session.add(new_user)
    db.session.commit()

    token = generate_token(new_user.id)
    return token, None

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        return None, 'Invalid credentials'

    token = generate_token(user.id)
    return token, None
