def register():
from flask import Blueprint, request, jsonify, render_template
from ..controllers.auth_controller import register_user, login_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    data = request.get_json() if request.is_json else request.form.to_dict()
    user = register_user(data)
    return jsonify({'user_id': user['id']}), 201


def login():
@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    data = request.get_json() if request.is_json else request.form.to_dict()
    token = login_user(data)
    return jsonify({'token': token})
