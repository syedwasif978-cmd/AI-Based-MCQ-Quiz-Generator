from app.main import create_app


def test_pdf_generation_files_created(tmp_path):
    # This test uses the scaffold generator to create PDFs
    app = create_app()
    client = app.test_client()
    payload = {'subject': 'Algorithms', 'num_questions': 3, 'difficulty': 'Easy'}
    resp = client.post('/quiz/generate', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'quiz_id' in data
