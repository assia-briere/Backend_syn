from flask import Blueprint, request, jsonify
from services.auth_service import register_user, authenticate_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    token, error = register_user(data['username'], data['email'], data['password'])
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'token': token})

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    token, error = authenticate_user(data['email'], data['password'])
    if error:
        return jsonify({'error': error}), 401
    return jsonify({'token': token})
