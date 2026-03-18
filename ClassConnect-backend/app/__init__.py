import os
from flask import Flask, jsonify
from .extensions import db, migrate, cors, jwt
from .routes import register_blueprints
from .utils import register_error_handlers
from .auth import add_jwt_callbacks

def create_app():
    app = Flask(__name__, instance_relative_config=False)

    env = os.getenv("FLASK_ENV", "development")
    from config import config_by_name
    app.config.from_object(config_by_name.get(env, config_by_name["development"]))

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    jwt.init_app(app)
    add_jwt_callbacks(jwt)

    @app.get("/")
    def root():
        return jsonify({"ok": True, "service": "ClassConnect API", "env": env})

    register_blueprints(app)
    register_error_handlers(app)

    return app
