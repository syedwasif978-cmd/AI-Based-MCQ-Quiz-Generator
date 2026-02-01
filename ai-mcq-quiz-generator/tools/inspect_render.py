from app.main import create_app
app=create_app()
with app.app_context():
    from flask import render_template
    out = render_template('dashboard.html')
    print(out[:800])
