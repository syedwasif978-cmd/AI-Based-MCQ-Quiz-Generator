import os
import json
import re

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'generated_pdfs', 'logs'))

files = [f for f in os.listdir(LOG_DIR) if f.startswith('gemini_raw_')]
files.sort()
if not files:
    print('No gemini_raw files found')
    raise SystemExit(1)

latest = files[-1]
path = os.path.join(LOG_DIR, latest)
print('Validating', path)
text = open(path, 'r', encoding='utf-8').read()

m = re.search(r"<<<JSON>>>([\s\S]*?)<<<END_JSON>>>", text, re.IGNORECASE)
if not m:
    print('No markers found - attempting to extract from braces')
    first = text.find('{')
    last = text.rfind('}')
    if first == -1 or last == -1:
        print('No JSON-like block found')
        raise SystemExit(2)
    candidate = text[first:last+1]
else:
    candidate = m.group(1).strip()

try:
    j = json.loads(candidate)
except Exception as e:
    print('JSON parse error:', e)
    # try cleanup steps
    cleaned = candidate
    cleaned = re.sub(r",\s*([\}\]])", r"\1", cleaned)
    cleaned = cleaned.replace('“', '"').replace('”', '"').replace('`', '"')
    try:
        j = json.loads(cleaned)
        print('Parsed after cleanup')
    except Exception as e2:
        print('Still failed after cleanup:', e2)
        raise SystemExit(3)

# Basic schema validation
questions = j.get('questions')
answers = j.get('answers')
if not isinstance(questions, list):
    print('questions is not a list')
    raise SystemExit(4)
if not isinstance(answers, list):
    print('answers is not a list')
    raise SystemExit(5)

ids = set()
valid = True
for q in questions:
    if 'id' not in q or 'q' not in q or 'options' not in q:
        print('Question missing fields:', q)
        valid = False
        continue
    if not isinstance(q['options'], list) or len(q['options']) != 4:
        print('Question options invalid length:', q.get('id'))
        valid = False
    ids.add(q['id'])

for a in answers:
    if 'id' not in a or 'answer' not in a:
        print('Answer missing fields:', a)
        valid = False
        continue
    if a['id'] not in ids:
        print('Answer id not in questions:', a['id'])
        valid = False
    if a['answer'] not in ('A','B','C','D'):
        print('Answer not A-D:', a)
        valid = False

if valid:
    print('JSON structure OK: questions=', len(questions), 'answers=', len(answers))
else:
    print('JSON structure FAILED')
    raise SystemExit(6)
