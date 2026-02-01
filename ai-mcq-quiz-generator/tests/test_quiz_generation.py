from app.main import create_app


def test_generate_quiz_endpoint():
    app = create_app()
    client = app.test_client()
    payload = {'subject': 'Data Structures', 'num_questions': 5, 'difficulty': 'Medium'}
    resp = client.post('/quiz/generate', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'quiz_id' in data
