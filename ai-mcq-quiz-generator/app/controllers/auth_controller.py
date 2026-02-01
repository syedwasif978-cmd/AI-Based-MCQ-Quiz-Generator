from werkzeug.security import generate_password_hash, check_password_hash
from ..services.user_service import create_user, find_user_by_email


def register_user(data):
    user = create_user(data)
    return user


def login_user(data):
    user = find_user_by_email(data.get('email'))
    if not user:
        raise Exception('Invalid credentials')
    if not check_password_hash(user['password_hash'], data.get('password')):
        raise Exception('Invalid credentials')
    # For scaffold, return a dummy token
    return 'dummy-token'
