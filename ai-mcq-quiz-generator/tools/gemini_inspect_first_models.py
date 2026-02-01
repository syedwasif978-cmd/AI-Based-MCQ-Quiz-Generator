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
    models = genai.list_models()
    for i, m in enumerate(models, start=1):
        if i > 25:
            break
        print('\n--- MODEL', i, '---')
        try:
            print('repr:', repr(m)[:400])
        except Exception:
            pass
        try:
            attrs = [a for a in dir(m) if not a.startswith('_')]
            print('attrs sample:', attrs[:40])
        except Exception:
            pass
        try:
            # try attribute access
            if hasattr(m, 'supported_generation_methods'):
                print('supported_generation_methods:', getattr(m, 'supported_generation_methods'))
            if hasattr(m, 'supportedMethods'):
                print('supportedMethods:', getattr(m, 'supportedMethods'))
            if hasattr(m, 'capabilities'):
                print('capabilities:', getattr(m, 'capabilities'))
            if hasattr(m, 'display_name'):
                print('display_name:', getattr(m, 'display_name'))
            if hasattr(m, 'name'):
                print('name:', getattr(m, 'name'))
            if hasattr(m, 'description'):
                print('description:', getattr(m, 'description')[:200])
        except Exception as e:
            print('attribute access error', e)
except Exception as e:
    print('Error listing Gemini models:', e)
    raise SystemExit(1)
