def validate_quiz_payload(data):
    errors = []
    num = data.get('num_questions')
    if not num or int(num) < 5 or int(num) > 50:
        errors.append('num_questions must be between 5 and 50')
    difficulty = data.get('difficulty')
    if difficulty not in ['Easy', 'Medium', 'Hard']:
        errors.append('difficulty must be Easy, Medium, or Hard')
    return errors
