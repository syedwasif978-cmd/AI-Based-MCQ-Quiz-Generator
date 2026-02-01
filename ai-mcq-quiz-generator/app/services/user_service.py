from ..database.db import get_session
from ..models.user import User


def create_user(data):
    # Minimal scaffold: return dict; integrate with DB later
    user = {
        'id': 1,
        'full_name': data.get('full_name'),
        'email': data.get('email'),
        'password_hash': data.get('password')
    }
    return user


def find_user_by_email(email):
    # scaffold stub
    if email == 'test@uni.edu':
        return {'id': 1, 'email': 'test@uni.edu', 'password_hash': 'pbkdf2:sha256:150000$abc$abc'}
    return None
