import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    FERNET_KEY = os.getenv('FERNET_KEY')
    # Google Gemini API key for MCQ generation
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    UPLOAD_FOLDER = 'generated_pdfs'

    UPLOAD_FOLDER = 'generated_pdfs'
