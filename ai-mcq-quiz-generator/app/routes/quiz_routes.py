from flask import Blueprint, request, jsonify
from ..controllers.quiz_controller import generate_quiz

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')


@quiz_bp.route('/generate', methods=['POST'])
def generate():
    data = request.json
    quiz = generate_quiz(data)
    return jsonify({'quiz_id': quiz['id']}), 201
