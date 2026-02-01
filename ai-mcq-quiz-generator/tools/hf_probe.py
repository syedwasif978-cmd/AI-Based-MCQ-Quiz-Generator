import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('HUGGINGFACE_API_KEY')
model = os.getenv('HUGGINGFACE_MODEL')
print('Using model:', model)
headers = {'Authorization': f'Bearer {key}'}
urls = [f'https://router.huggingface.co/models/{model}', f'https://api-inference.huggingface.co/models/{model}']
for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=20)
        print('\nURL:', url)
        print('Status code:', r.status_code)
        try:
            print('JSON:', r.json())
        except Exception:
            print('Text:', r.text[:1000])
    except Exception as e:
        print('Error contacting', url, type(e).__name__, e)
