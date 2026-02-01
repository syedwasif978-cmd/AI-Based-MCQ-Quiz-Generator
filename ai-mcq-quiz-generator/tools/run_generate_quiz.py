from app.services.quiz_service import create_and_generate_quiz

params = {
    'subject': 'Calculus',
    'topics': 'derivatives, integration',
    'num_questions': 6,
    'difficulty': 'Medium',
    'time_limit': 25,
    'professor_id': 1
}

quiz = create_and_generate_quiz(params)
print('Created quiz:', quiz)
# Print stored quiz details
from app.services.quiz_service import QUIZ_STORE
print('QUIZ_STORE:', QUIZ_STORE)
