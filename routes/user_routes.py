from flask import Blueprint, request, jsonify
from models.user import User
from database import db
from utils.jwt_utils import decode_token

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/profile', methods=['GET'])
def get_profile():
    token = request.headers.get('Authorization')
    user_id = decode_token(token)
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at
    })
