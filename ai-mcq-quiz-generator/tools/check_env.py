import os
from dotenv import load_dotenv

load_dotenv()

keys = [
    'OPENAI_API_KEY',
    'OPENAI_MODEL',
    'HUGGINGFACE_API_KEY',
    'HUGGINGFACE_MODEL',
    'DATABASE_URL',
    'FERNET_KEY',
    'SECRET_KEY',
    'ORACLE_INSTANT_CLIENT_PATH'
]

print('Environment key presence (values are NOT printed):')
for k in keys:
    v = os.getenv(k)
    print(f" - {k}: {'SET' if v else 'NOT SET'}")

# Helpful note
print('\nTip: If OPENAI_API_KEY is SET, the app will attempt to call OpenAI; check app logs for "[ai_client] Attempting OpenAI generation" or "[ai_client] Received valid JSON from OpenAI".')
