from flask import Flask
from .config import Config
from .database.db import init_db


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # initialize DB (SQLAlchemy) and others
    init_db(app)

    # register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.quiz_routes import quiz_bp
    from .routes.pdf_routes import pdf_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(pdf_bp)

    # Root route — show dashboard
    @app.route('/')
    def index():
        try:
            from flask import render_template
            return render_template('dashboard.html')
        except Exception:
            return ('<h1>AI MCQ Quiz Generator</h1><p>Use the API endpoints to interact with the app.</p>')

    return app


if __name__ == '__main__':
    # Allow running this module directly: python app/main.py
    application = create_app()
    application.run(debug=True, host='0.0.0.0', port=5000)
