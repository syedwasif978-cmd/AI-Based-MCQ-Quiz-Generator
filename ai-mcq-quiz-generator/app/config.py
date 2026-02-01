import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    FERNET_KEY = os.getenv('FERNET_KEY')
    UPLOAD_FOLDER = 'generated_pdfs'
