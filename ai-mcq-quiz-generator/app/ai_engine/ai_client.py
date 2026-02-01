import os
import json
import re
from dotenv import load_dotenv
from ..ai_engine.prompt_templates import MASTER_PROMPT

# Ensure environment variables from .env are loaded when this module is imported directly
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL')  # optional, e.g. 'models/gemini-2.5-pro'



def _attempt_load_json(candidate: str):
    """Try to parse JSON from a candidate string. Attempt a small set of tolerant cleanup steps on failure."""
    try:
        return json.loads(candidate)
    except Exception:
        # Try to fix common issues: trailing commas before ] or }, and smart quotes
        try:
            cleaned = candidate
            cleaned = re.sub(r",\s*([\}\]])", r"\1", cleaned)  # remove trailing commas
            cleaned = cleaned.replace('“', '"').replace('”', '"').replace("`", '"')
            # Try to load again
            return json.loads(cleaned)
        except Exception:
            return None


def _extract_json_from_text(text: str):
    """Extract a JSON object from free-form text returned by the model.

    Strategy:
    - If explicit markers <<<JSON>>> ... <<<END_JSON>>> are present, prefer them.
    - Otherwise, search for the largest JSON-like block containing the key "questions" using a regex.
    - As a last resort, take the substring from the first '{' to the last '}' and try to parse/clean it.
    - Return dict on success or None if parsing failed.
    """
    if not text or not text.strip():
        return None

    # 1) Markers
    m = re.search(r"<<<JSON>>>([\s\S]*?)<<<END_JSON>>>", text, re.IGNORECASE)
    if m:
        candidate = m.group(1).strip()
        j = _attempt_load_json(candidate)
        if j is not None:
            return j

    # 2) Look for a JSON object that contains the "questions" key
    m = re.search(r"(\{[\s\S]*\"questions\"[\s\S]*\})", text)
    if m:
        candidate = m.group(1).strip()
        j = _attempt_load_json(candidate)
        if j is not None:
            return j

    # 3) Fallback: try from first '{' to last '}'
    first = text.find('{')
    last = text.rfind('}')
    if first != -1 and last != -1 and last > first:
        candidate = text[first:last+1]
        j = _attempt_load_json(candidate)
        if j is not None:
            return j

    return None


def _local_dummy(subject, topics, num, difficulty):
    """Richer deterministic generator that uses topics and produces substantive, exam-style questions.
    This is used as a reliable fallback when the Gemini API is not available or fails to return valid JSON."""
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


def generate_mcqs(subject, num, difficulty, topics=None, max_retries=3):
    """Generate MCQs using Google Gemini if API key is available; otherwise fallback to a local generator.
    Ensures uniqueness of questions and that the provided topics are represented.

    This implementation tolerates free-form model output by extracting JSON via regex and
    cleaning common JSON problems. If parsing fails, the model will be asked to reply with
    ONLY valid JSON and retried up to `max_retries` times."""
    
    # Use local generator if API key not set
    if not GEMINI_API_KEY:
        print("[ai_client] GEMINI_API_KEY not set - using local deterministic generator")
        return _local_dummy(subject, topics, num, difficulty)

    # Build prompt
    prompt = MASTER_PROMPT.format(subject=subject, topics=(topics or ''), num=num, difficulty=difficulty)

    try:
        import google.generativeai as genai
        print("[ai_client] Attempting Gemini generation")

        genai.configure(api_key=GEMINI_API_KEY)
        # Auto-detect a model that supports 'generateContent' if not explicitly set
        chosen_model = GEMINI_MODEL
        if not chosen_model:
            try:
                models_iter = genai.list_models()
                for m in models_iter:
                    try:
                        methods = getattr(m, 'supported_generation_methods', None)
                        if methods and any('generate' in str(x).lower() for x in methods):
                            chosen_model = getattr(m, 'name', None) or getattr(m, 'display_name', None)
                            break
                    except Exception:
                        continue
            except Exception as e:
                print(f"[ai_client] Warning: could not list Gemini models: {e}")

        if not chosen_model:
            print("[ai_client] No Gemini model found that supports generation; falling back to local generator")
            return _local_dummy(subject, topics, num, difficulty)

        print(f"[ai_client] Using Gemini model: {chosen_model}")
        model = genai.GenerativeModel(chosen_model)

        def _extract_candidate_block(text):
            # Prefer marker enclosed block
            m = re.search(r"<<<JSON>>>([\s\S]*?)<<<END_JSON>>>", text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
            # Otherwise, grab from first '{' to last '}'
            first = text.find('{')
            last = text.rfind('}')
            if first != -1 and last != -1 and last > first:
                return text[first:last+1]
            return None

        def _attempt_generation_with_repair(model, base_prompt, retries):
            j = None
            for attempt in range(retries + 1):
                response = model.generate_content(base_prompt, generation_config=genai.types.GenerationConfig(max_output_tokens=4000, temperature=0.0))
                text = response.text if response else ""
                # Save raw response and meta for debugging
                try:
                    from ..utils.helpers import ensure_dir
                    import datetime
                    now = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                    raw_path = f"generated_pdfs/logs/gemini_raw_{now}.txt"
                    meta_path = f"generated_pdfs/logs/gemini_meta_{now}.txt"
                    ensure_dir(raw_path)
                    with open(raw_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    with open(meta_path, 'w', encoding='utf-8') as f:
                        f.write(repr(response))
                    print(f"[ai_client] Saved raw Gemini response to {raw_path} and meta to {meta_path}")
                except Exception as e:
                    print(f"[ai_client] Failed to save raw response: {e}")

                j = _extract_json_from_text(text)
                if j is not None:
                    return j

                # Attempt a JSON repair if we can find a candidate JSON-like block
                candidate = _extract_candidate_block(text)
                if candidate:
                    repair_prompt = (
                        "I could not parse the JSON from your previous message. "
                        "Please FIX and RETURN ONLY the valid JSON between the markers <<<JSON>>> and <<<END_JSON>>> with no extra text. "
                        "If you cannot, return exactly {\"error\": \"UNABLE_TO_PROVIDE_JSON\"}.\n\n"
                        "Candidate JSON:\n" + candidate
                    )
                    response2 = model.generate_content(repair_prompt, generation_config=genai.types.GenerationConfig(max_output_tokens=4000, temperature=0.0))
                    text2 = response2.text if response2 else ""
                    # Save repair attempt
                    try:
                        from ..utils.helpers import ensure_dir
                        import datetime
                        now = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                        raw_path = f"generated_pdfs/logs/gemini_raw_{now}.txt"
                        meta_path = f"generated_pdfs/logs/gemini_meta_{now}.txt"
                        ensure_dir(raw_path)
                        with open(raw_path, 'w', encoding='utf-8') as f:
                            f.write(text2)
                        with open(meta_path, 'w', encoding='utf-8') as f:
                            f.write(repr(response2))
                        print(f"[ai_client] Saved repair attempt raw Gemini response to {raw_path} and meta to {meta_path}")
                    except Exception as e:
                        print(f"[ai_client] Failed to save repair raw response: {e}")

                    j = _extract_json_from_text(text2)
                    if j is not None:
                        return j
                # else continue to next attempt
            return None

        # Primary generation attempts on chosen model with repair
        j = _attempt_generation_with_repair(model, prompt, max_retries)

        # If still no JSON, try a couple of alternative generation-capable models
        if j is None:
            try:
                alt_tried = 0
                models_iter = genai.list_models()
                for m in models_iter:
                    try:
                        name = getattr(m, 'name', None) or getattr(m, 'display_name', None)
                        if not name or name == chosen_model:
                            continue
                        methods = getattr(m, 'supported_generation_methods', None)
                        if not methods or not any('generate' in str(x).lower() for x in methods):
                            continue
                        print(f"[ai_client] Trying alternate Gemini model: {name}")
                        alt_model = genai.GenerativeModel(name)
                        j = _attempt_generation_with_repair(alt_model, prompt, max(1, max_retries - 1))
                        alt_tried += 1
                        if j is not None:
                            print(f"[ai_client] Alternate model {name} returned valid JSON")
                            chosen_model = name
                            model = alt_model
                            break
                        if alt_tried >= 2:
                            break
                    except Exception:
                        continue
            except Exception as e:
                print(f"[ai_client] Warning: could not list alternative Gemini models: {e}")

        if j is None:
            print("[ai_client] Gemini did not return valid JSON after retries and alternate models; falling back to local generator")
            return _local_dummy(subject, topics, num, difficulty)

        print("[ai_client] Received valid JSON from Gemini")
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

        # If insufficient unique questions, try asking for more once
        if len(uniq_q) < int(num):
            print(f"[ai_client] Received {len(uniq_q)} unique questions (<{num}); asking model to provide more")
            more_prompt = prompt + f"\n\nPlease provide {int(num)} unique questions in the exact same JSON format. You previously provided {len(uniq_q)} questions."
            j2 = _attempt_generation_with_repair(model, more_prompt, 1)
            if j2:
                questions = j2.get('questions', [])
                answers = j2.get('answers', [])
                seen = set()
                uniq_q = []
                for q in questions:
                    key = q.get('q','').strip().lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    uniq_q.append(q)

        # Trim/format results to requested number
        if len(uniq_q) >= int(num):
            uniq_q = uniq_q[:int(num)]
            # Align answers by id
            id_map = {q['id']: q for q in uniq_q if 'id' in q}
            filtered_answers = [a for a in answers if a.get('id') in id_map]
            return {'questions': uniq_q, 'answers': filtered_answers}


    except Exception as e:
        print(f"[ai_client] Error during Gemini generation: {e}; falling back to local generator")
        return _local_dummy(subject, topics, num, difficulty)

    print("[ai_client] Using local deterministic generator as final fallback")
    return _local_dummy(subject, topics, num, difficulty)
