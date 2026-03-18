from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from .extensions import db
from .models import User, ProfessorProfile
from .schemas import user_schema
from .utils import api_response

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.post("/register")
def register():
    payload = request.get_json() or {}
    email = (payload.get("email") or "").lower().strip()
    name = (payload.get("name") or "").strip()
    password = payload.get("password") or ""
    role = (payload.get("role") or "student").strip()

    if not email or not name or not password:
        return api_response(None, "email, name, password are required", 400)

    if User.query.filter_by(email=email).first():
        return api_response(None, "email already registered", 409)

    u = User(email=email, name=name, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.flush()

    if role == "professor":
        prof = ProfessorProfile(user_id=u.id, department=payload.get("department"), cabin_location=payload.get("cabin_location"))
        db.session.add(prof)

    db.session.commit()
    return api_response(user_schema.dump(u), "registered", 201)

@auth_bp.post("/login")
def login():
    payload = request.get_json() or {}
    email = (payload.get("email") or "").lower().strip()
    password = payload.get("password") or ""

    u = User.query.filter_by(email=email).first()
    if not u or not u.check_password(password):
        return api_response(None, "invalid credentials", 401)

    token = create_access_token(
    identity=str(u.id),
    additional_claims={"role": u.role}
)
    return api_response({"token": token, "user": user_schema.dump(u)}, "ok")

def add_jwt_callbacks(jwt):
    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        return identity
