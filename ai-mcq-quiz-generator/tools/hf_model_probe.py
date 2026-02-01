import os, requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('HUGGINGFACE_API_KEY')
models = ['gpt2','distilgpt2','google/flan-t5-large','google/flan-t5-base','bigscience/bloom','tiiuae/falcon-7b-instruct','meta-llama/Llama-2-7b-chat','databricks/dolly-v2-3b']
headers = {'Authorization': f'Bearer {key}'}
for model in models:
    for url in [f'https://router.huggingface.co/models/{model}', f'https://api-inference.huggingface.co/models/{model}']:
        try:
            r = requests.get(url, headers=headers, timeout=20)
            print(model, url, r.status_code)
        except Exception as e:
            print('error', model, url, type(e).__name__, e)
