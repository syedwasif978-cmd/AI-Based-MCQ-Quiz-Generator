from app.main import create_app


def test_register_endpoint():
    app = create_app()
    client = app.test_client()
    resp = client.post('/auth/register', json={
        'full_name': 'Test', 'email': 't@u.edu', 'password': 'pw'
    })
    assert resp.status_code == 201
