from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..schemas import user_schema
from ..models import User, ProfessorProfile
from ..utils import api_response, current_user_id, current_user_role
from ..extensions import db

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.get("/me")
@jwt_required()
def me():
    u = User.query.get_or_404(current_user_id())
    return api_response(user_schema.dump(u))


@users_bp.get("/professors")
def list_professors():
    professors = User.query.filter_by(role="professor").order_by(User.name.asc()).all()

    result = []
    for prof in professors:
        profile = ProfessorProfile.query.filter_by(user_id=prof.id).first()
        result.append({
            "id": prof.id,
            "name": prof.name,
            "email": prof.email,
            "role": prof.role,
            "department": profile.department if profile else None,
            "cabin_location": profile.cabin_location if profile else None
        })

    return api_response(result)


@users_bp.post("/update-location")
@jwt_required()
def update_location():
    if current_user_role() != "professor":
        return api_response(None, "Only professors can update location", 403)

    data = request.get_json() or {}
    new_location = (data.get("cabin_location") or "").strip()

    if not new_location:
        return api_response(None, "cabin_location is required", 400)

    profile = ProfessorProfile.query.filter_by(user_id=current_user_id()).first()
    if not profile:
        return api_response(None, "Professor profile not found", 404)

    profile.cabin_location = new_location
    db.session.commit()

    return api_response(
        {"cabin_location": profile.cabin_location},
        "Location updated successfully"
    )