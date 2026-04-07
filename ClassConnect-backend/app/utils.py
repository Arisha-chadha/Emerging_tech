from flask import jsonify
from werkzeug.exceptions import HTTPException
from flask_jwt_extended import get_jwt_identity, get_jwt

def api_response(data=None, message="", status=200):
    return jsonify({"data": data, "message": message}), status

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        return api_response(None, e.description, e.code)

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):
        return api_response(None, str(e), 500)

def current_user_id():
    ident = get_jwt_identity()
    return int(ident) if ident is not None else None

def current_user_role():
    claims = get_jwt() or {}
    role = claims.get("role")
    return role.strip().lower() if isinstance(role, str) else None