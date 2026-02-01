from flask import Flask
import sys
import os

try:
    # Normal package import when run via run.py or as a package
    from .config import Config
    from .database.db import init_db
except Exception:
    # Support running this file directly: add project root to sys.path and import package modules
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from app.config import Config
    from app.database.db import init_db


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # initialize DB (SQLAlchemy) and others
    init_db(app)

    # register blueprints (support package or direct script import)
    try:
        from .routes.auth_routes import auth_bp
        from .routes.quiz_routes import quiz_bp
        from .routes.pdf_routes import pdf_bp
    except Exception:
        from app.routes.auth_routes import auth_bp
        from app.routes.quiz_routes import quiz_bp
        from app.routes.pdf_routes import pdf_bp

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
