from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from ..controllers.quiz_controller import generate_quiz

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')


@quiz_bp.route('/generate', methods=['GET', 'POST'])
def generate():
    # GET -> render form; POST -> accept JSON or form data
    if request.method == 'GET':
        return render_template('quiz_form.html')

    # POST handling
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        # form submission
        data = {
            'subject': request.form.get('subject'),
            'topics': request.form.get('topics'),
            'num_questions': request.form.get('num_questions'),
            'difficulty': request.form.get('difficulty'),
            'professor_id': request.form.get('professor_id', 1),
            'time_limit': request.form.get('time_limit')
        }

    quiz = generate_quiz(data)

    # If form submission, render preview page with download links
    if not request.is_json:
        return render_template('quiz_preview.html', quiz_id=quiz['id'])

    return jsonify({'quiz_id': quiz['id']}), 201
