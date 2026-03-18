from flask import Flask
from .health import health_bp
from ..auth import auth_bp
from .users import users_bp
from .availability import availability_bp
from .meetings import meetings_bp
from .messages import messages_bp
from .resources import resources_bp

def register_blueprints(app: Flask):
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(availability_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(resources_bp)
