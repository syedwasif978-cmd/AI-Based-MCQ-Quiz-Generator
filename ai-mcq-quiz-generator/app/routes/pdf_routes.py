from flask import Blueprint, send_file, abort
from ..controllers.pdf_controller import get_question_pdf_path, get_answer_pdf_path

pdf_bp = Blueprint('pdf', __name__, url_prefix='/pdf')


@pdf_bp.route('/questions/<int:quiz_id>', methods=['GET'])
def questions_pdf(quiz_id):
    path = get_question_pdf_path(quiz_id)
    if not path:
        abort(404)
    return send_file(path, as_attachment=True)


@pdf_bp.route('/answers/<int:quiz_id>', methods=['GET'])
def answers_pdf(quiz_id):
    path = get_answer_pdf_path(quiz_id)
    if not path:
        abort(404)
    return send_file(path, as_attachment=True)
