from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.main.config import configurations

# Initialize SQLAlchemy database
db = SQLAlchemy()


def create_app(config):
    # Check if configuration is valid
    if config not in configurations:
        raise ValueError(f'{config} is not a valid configuration.')

    # Create Flask application and initialize SQLAlchemy with the application instance
    app = Flask(__name__)
    app.config.from_object(configurations[config])
    db.init_app(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app
