import os
import json
from ..ai_engine.prompt_templates import MASTER_PROMPT

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def generate_mcqs(subject, num, difficulty):
    # Scaffold: returns deterministic dummy content for offline dev and testing
    questions = []
    answers = []
    for i in range(1, int(num) + 1):
        questions.append({
            'id': i,
            'q': f"Sample question {i} on {subject} (Difficulty: {difficulty})",
            'options': ["Option A","Option B","Option C","Option D"]
        })
        answers.append({'id': i, 'answer': 'B'})

    return {'questions': questions, 'answers': answers}

    # For production, swap above with OpenAI/api call and JSON parsing
    # Example:
    # prompt = MASTER_PROMPT.format(subject=subject, num=num, difficulty=difficulty)
    # call provider and parse JSON
