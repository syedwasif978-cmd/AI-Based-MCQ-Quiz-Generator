from flask import Blueprint, request, jsonify
from ..controllers.auth_controller import register_user, login_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    user = register_user(data)
    return jsonify({'user_id': user['id']}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    token = login_user(data)
    return jsonify({'token': token})
