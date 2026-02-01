import os
import json
from datetime import datetime
from ..ai_engine.ai_client import generate_mcqs
from ..pdf_generator.question_paper import generate_questions_pdf
from ..pdf_generator.answer_key import generate_answers_pdf

# For scaffold, we store generated filepaths in-memory
QUIZ_STORE = {}


def create_and_generate_quiz(data):
    # data: subject, topics, num_questions, difficulty, professor_id
    subject = data.get('subject')
    topics = data.get('topics')
    num = data.get('num_questions', 10)
    difficulty = data.get('difficulty', 'Medium')

    generated = generate_mcqs(subject, num, difficulty, topics=topics)
    now = datetime.utcnow().strftime('%Y_%m_%d_%H%M%S')
    questions_rel = f"generated_pdfs/questions/quiz_{now}.pdf"
    answers_rel = f"generated_pdfs/answers/answer_key_{now}.pdf"

    questions_pdf = generate_questions_pdf(generated['questions'], questions_rel, subject, difficulty, time_limit=data.get('time_limit'))
    answers_pdf = generate_answers_pdf(generated['answers'], answers_rel, subject)

    quiz_id = len(QUIZ_STORE) + 1
    QUIZ_STORE[quiz_id] = {'questions': questions_pdf, 'answers': answers_pdf, 'meta': data}
    # Log created files for debugging
    print(f"[quiz_service] Created quiz {quiz_id}: questions={questions_pdf}, answers={answers_pdf}")
    return {'id': quiz_id}


def get_quiz_paths(quiz_id):
    return QUIZ_STORE.get(quiz_id)
