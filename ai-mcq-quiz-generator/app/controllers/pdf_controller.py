from ..services.quiz_service import get_quiz_paths


def get_question_pdf_path(quiz_id):
    paths = get_quiz_paths(quiz_id)
    return paths.get('questions')


def get_answer_pdf_path(quiz_id):
    paths = get_quiz_paths(quiz_id)
    return paths.get('answers')
