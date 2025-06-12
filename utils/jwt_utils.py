import jwt
from datetime import datetime, timedelta
from config import JWT_SECRET

# Generate token
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)  # Set expiration time
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

# Decode token
def decode_token(token):
    try:
        # Decode the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']  # Return the user_id from the payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
