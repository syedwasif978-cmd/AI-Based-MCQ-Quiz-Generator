from ..services.quiz_service import create_and_generate_quiz


def generate_quiz(data):
    quiz = create_and_generate_quiz(data)
    return quiz
