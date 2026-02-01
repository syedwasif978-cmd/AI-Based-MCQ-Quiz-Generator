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

    return app
