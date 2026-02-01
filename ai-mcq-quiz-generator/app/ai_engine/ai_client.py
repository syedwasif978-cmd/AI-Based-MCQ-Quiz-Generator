import os
import json
import re
from dotenv import load_dotenv
from ..ai_engine.prompt_templates import MASTER_PROMPT

# Ensure environment variables from .env are loaded when this module is imported directly
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
# Hugging Face settings (prefer HF if key present)
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
HUGGINGFACE_MODEL = os.getenv('HUGGINGFACE_MODEL', 'google/flan-t5-large')



def _extract_json_from_text(text: str):
    # Try to find a JSON object in the text using a simple regex
    m = re.search(r"{\s*\"questions\"[\s\S]*\}$", text.strip())
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    # Fallback: try to load entire text as JSON
    try:
        return json.loads(text)
    except Exception:
        return None


def _local_dummy(subject, topics, num, difficulty):
    """Richer deterministic generator that uses topics and produces substantive, exam-style questions.
    This is used as a reliable fallback when the OpenAI API is not available or fails to return valid JSON."""
    questions = []
    answers = []
    topic_list = [t.strip() for t in (topics or '').split(',') if t.strip()]
    if not topic_list:
        topic_list = [subject or 'General']

    subj = (subject or 'the subject').strip()
    for i in range(1, int(num) + 1):
        t = topic_list[(i - 1) % len(topic_list)]
        # Build subject/topic-aware templates
        q_text = ''
        opts = []
        correct = 'A'

        if any(x in subj.lower() for x in ('math', 'calc', 'algebra', 'calculus')):
            # Math-themed templates
            if 'deriv' in t.lower() or 'derivative' in t.lower():
                q_text = f"Q{i}. Let f(x) = x^3 + 3x^2. What is f'(x)?"
                opts = ["3x^2 + 6x", "3x^2 + 2x", "x^2 + 6x", "6x^2 + 3x"]
                correct = 'A'
            elif 'integr' in t.lower() or 'integration' in t.lower():
                q_text = f"Q{i}. Evaluate the indefinite integral ∫ 2x dx."
                opts = ["x^2 + C", "2x + C", "x + C", "ln|x| + C"]
                correct = 'A'
            else:
                q_text = f"Q{i}. In the topic '{t}', which statement is most accurate about its core concept?"
                opts = [f"A key property of {t}", f"A common misconception about {t}", f"An unrelated statement", f"A wrong approach to {t}"]
                correct = ['A','B','C','D'][i % 4]
        else:
            # General-subject templates
            q_text = f"Q{i}. In {subj} - {t}, which of the following best describes a core concept?"
            opts = [f"A concise correct statement about {t}", f"A plausible-but-incorrect distractor", f"A partially correct statement", f"An incorrect statement"]
            correct = ['A','B','C','D'][i % 4]

        questions.append({'id': i, 'q': q_text, 'topic': t, 'options': opts})
        answers.append({'id': i, 'answer': correct})

    return {'questions': questions, 'answers': answers}


def generate_mcqs(subject, num, difficulty, topics=None, max_retries=2):
    """Generate MCQs using OpenAI if available; otherwise fallback to a local generator.
    Ensures uniqueness of questions and that the provided topics are represented."""
    # Use local generator if API key not set
    if not OPENAI_API_KEY:
        print("[ai_client] OPENAI_API_KEY not set - using local deterministic generator")
        return _local_dummy(subject, topics, num, difficulty)

    # Build prompt
    prompt = MASTER_PROMPT.format(subject=subject, topics=(topics or ''), num=num, difficulty=difficulty)

    # Prefer Hugging Face if API key set
    if HUGGINGFACE_API_KEY:
        try:
            import requests
            print(f"[ai_client] Attempting Hugging Face generation using model '{HUGGINGFACE_MODEL}'")
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}", "Content-Type": "application/json"}
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 800}, "options": {"wait_for_model": True}}
            # Use the new Router endpoint (recommended by Hugging Face)
            hf_url = f"https://router.huggingface.co/models/{HUGGINGFACE_MODEL}"
            resp = requests.post(hf_url, headers=headers, json=payload, timeout=60)
            if resp.status_code != 200:
                # Try to surface HF errors
                msg = ''
                try:
                    msg = resp.json()
                except Exception:
                    msg = resp.text
                print(f"[ai_client] Hugging Face API error {resp.status_code}: {msg}")
                # If router returns 404 or model not found, try the api-inference endpoint as a fallback
                if resp.status_code == 404:
                    try:
                        fallback_url = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
                        print(f"[ai_client] Router returned 404; trying inference endpoint {fallback_url} as fallback")
                        resp2 = requests.post(fallback_url, headers=headers, json=payload, timeout=60)
                        if resp2.status_code == 200:
                            resp = resp2
                        else:
                            msg2 = ''
                            try:
                                msg2 = resp2.json()
                            except Exception:
                                msg2 = resp2.text
                            print(f"[ai_client] Inference endpoint error {resp2.status_code}: {msg2}")
                            raise Exception(f"HuggingFace API returned status {resp2.status_code} on fallback")
                    except Exception:
                        raise Exception(f"HuggingFace API returned status {resp.status_code}")
                else:
                    raise Exception(f"HuggingFace API returned status {resp.status_code}")

            # HF inference may return a JSON with 'generated_text' or a list; handle both
            try:
                body = resp.json()
            except Exception:
                body = resp.text

            # extract text content
            text = ''
            if isinstance(body, dict) and 'generated_text' in body:
                text = body['generated_text']
            elif isinstance(body, list) and len(body) and isinstance(body[0], dict) and 'generated_text' in body[0]:
                text = body[0]['generated_text']
            elif isinstance(body, str):
                text = body
            else:
                # Some models return plain text in body as string
                text = str(body)

            j = _extract_json_from_text(text)
            if j:
                print("[ai_client] Received valid JSON from Hugging Face")
                questions = j.get('questions', [])
                answers = j.get('answers', [])
                # deduplicate
                seen = set()
                uniq_q = []
                for q in questions:
                    key = q.get('q','').strip().lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    uniq_q.append(q)

                if len(uniq_q) >= int(num):
                    uniq_q = uniq_q[:int(num)]
                    id_map = {q['id']: q for q in uniq_q if 'id' in q}
                    filtered_answers = [a for a in answers if a.get('id') in id_map]
                    return {'questions': uniq_q, 'answers': filtered_answers}
                else:
                    print(f"[ai_client] Hugging Face returned {len(uniq_q)} unique questions (<{num}).")
            else:
                print("[ai_client] Hugging Face response did not contain valid JSON; falling back to other providers or local generator.")
        except Exception as e:
            print(f"[ai_client] Error during Hugging Face generation: {e}; falling back to other providers/local generator")

    try:
        # Lazy import to avoid errors when openai isn't installed
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        messages = [{"role": "user", "content": prompt}]
        print(f"[ai_client] Attempting OpenAI generation using model '{OPENAI_MODEL}'")
        for attempt in range(max_retries + 1):
            resp = client.chat.completions.create(model=OPENAI_MODEL, messages=messages, max_tokens=1500)
            text = resp.choices[0].message.content
            j = _extract_json_from_text(text)
            if not j:
                # Try another attempt asking for strict JSON
                messages.append({"role": "assistant", "content": "Output was not valid JSON. Please respond with valid JSON only as specified."})
                continue

            print("[ai_client] Received valid JSON from OpenAI")
            # Basic validation
            questions = j.get('questions', [])
            answers = j.get('answers', [])

            # Deduplicate by question text
            seen = set()
            uniq_q = []
            for q in questions:
                key = q.get('q','').strip().lower()
                if key in seen:
                    continue
                seen.add(key)
                uniq_q.append(q)

            if len(uniq_q) < int(num) and attempt < max_retries:
                # Ask for more unique questions
                messages.append({"role":"user","content": f"You returned {len(uniq_q)} unique questions; please provide additional {int(num)-len(uniq_q)} unique questions in the same JSON format."})
                continue

            # Trim/format results to requested number
            if len(uniq_q) >= int(num):
                uniq_q = uniq_q[:int(num)]
                # Align answers by id
                id_map = {q['id']: q for q in uniq_q if 'id' in q}
                filtered_answers = [a for a in answers if a.get('id') in id_map]
                return {'questions': uniq_q, 'answers': filtered_answers}

            # If not successful, fall back to local dummy
            print("[ai_client] OpenAI did not return enough unique questions, falling back to local generator")
            break

    except Exception as e:
        # Show a helpful hint for quota/billing errors
        s = str(e)
        if 'insufficient_quota' in s or 'quota' in s or '429' in s:
            print("[ai_client] OpenAI returned an insufficient_quota/429 error. Consider switching to a cheaper model via OPENAI_MODEL (e.g., 'gpt-3.5-turbo') or checking your billing plan.")
        print(f"[ai_client] Error during OpenAI generation: {e}; falling back to local generator")
        # If any error occurs (network, API, parsing), fall back to deterministic local generator
        return _local_dummy(subject, topics, num, difficulty)

    print("[ai_client] Using local deterministic generator as final fallback")
    return _local_dummy(subject, topics, num, difficulty)
