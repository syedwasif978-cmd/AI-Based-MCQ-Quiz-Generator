import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print('GEMINI_API_KEY not set in environment (.env).')
    raise SystemExit(1)

try:
    import google.generativeai as genai
except Exception as e:
    print('google.generativeai library not available:', e)
    raise SystemExit(1)

try:
    genai.configure(api_key=GEMINI_API_KEY)
    print('Configured Gemini API')
    # Attempt to list models
    models = genai.list_models()
    print('Listing models (streamed):')
    print('\nModels with generation-related methods:')
    for i, m in enumerate(models, start=1):
        try:
            md = dict(m)
        except Exception:
            md = m
        methods = None
        try:
            methods = md.get('supported_generation_methods') or md.get('supportedMethods') or md.get('capabilities')
        except Exception:
            methods = None
        if methods:
            # normalize to list of strings
            try:
                method_list = [str(x).lower() for x in methods]
            except Exception:
                method_list = [str(methods).lower()]
            if any('generate' in s or 'bidi' in s or 'predict' in s for s in method_list):
                name = md.get('name') or md.get('displayName') or md.get('id') or md.get('model')
                print(f"\n[{i}] Model: {name}")
                print(' Supported methods:', method_list)
                print(' Entry summary:', {'display_name': md.get('display_name') or md.get('displayName'), 'description': md.get('description')})
    print('\n(End of filtered list)')
except Exception as e:
    print('Error listing Gemini models:', e)
    raise SystemExit(1)
