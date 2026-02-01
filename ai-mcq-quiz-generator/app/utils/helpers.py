import os

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
