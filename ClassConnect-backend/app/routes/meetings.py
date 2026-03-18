from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import Meeting
from ..schemas import meeting_schema, meetings_schema
from ..utils import api_response, current_user_id, current_user_role

meetings_bp = Blueprint("meetings", __name__, url_prefix="/api/meetings")

@meetings_bp.post("")
@jwt_required()
def create_meeting():
    if current_user_role() != "student":
        return api_response(None, "only students can request meetings", 403)

    payload = request.get_json() or {}
    try:
        meeting = Meeting(
            student_id=current_user_id(),
            professor_id=int(payload["professor_id"]),
            date=datetime.strptime(payload["date"], "%Y-%m-%d").date(),
            start_time=datetime.strptime(payload["start_time"], "%H:%M").time(),
            end_time=datetime.strptime(payload["end_time"], "%H:%M").time(),
            location=payload.get("location", "TBD"),
            agenda=payload.get("agenda", ""),
            status="pending",
        )
    except KeyError as e:
        return api_response(None, f"missing field {e}", 400)
    except Exception:
        return api_response(None, "bad date/time format", 400)

    db.session.add(meeting)
    db.session.commit()
    return api_response(meeting_schema.dump(meeting), "requested", 201)

@meetings_bp.get("/incoming")
@jwt_required()
def incoming_for_prof():
    if current_user_role() != "professor":
        return api_response(None, "only professors", 403)
    ms = Meeting.query.filter_by(professor_id=current_user_id()).order_by(Meeting.created_at.desc()).all()
    return api_response(meetings_schema.dump(ms))

@meetings_bp.get("/mine")
@jwt_required()
def my_meetings():
    role = current_user_role()
    uid = current_user_id()
    query = Meeting.query
    if role == "student":
        query = query.filter_by(student_id=uid)
    else:
        query = query.filter_by(professor_id=uid)
    ms = query.order_by(Meeting.date.desc(), Meeting.start_time.desc()).all()
    return api_response(meetings_schema.dump(ms))

@meetings_bp.post("/<int:meeting_id>/accept")
@jwt_required()
def accept_meeting(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)
    if current_user_role() != "professor" or m.professor_id != current_user_id():
        return api_response(None, "forbidden", 403)
    m.status = "confirmed"
    db.session.commit()
    return api_response(meeting_schema.dump(m), "accepted")

@meetings_bp.post("/<int:meeting_id>/reject")
@jwt_required()
def reject_meeting(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)
    if current_user_role() != "professor" or m.professor_id != current_user_id():
        return api_response(None, "forbidden", 403)
    m.status = "rejected"
    db.session.commit()
    return api_response(meeting_schema.dump(m), "rejected")

@meetings_bp.post("/<int:meeting_id>/reschedule")
@jwt_required()
def reschedule(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)
    if current_user_role() != "professor" or m.professor_id != current_user_id():
        return api_response(None, "forbidden", 403)
    payload = request.get_json() or {}
    if "date" in payload:
        m.date = datetime.strptime(payload["date"], "%Y-%m-%d").date()
    if "start_time" in payload:
        m.start_time = datetime.strptime(payload["start_time"], "%H:%M").time()
    if "end_time" in payload:
        m.end_time = datetime.strptime(payload["end_time"], "%H:%M").time()
    if "location" in payload:
        m.location = payload["location"]
    db.session.commit()
    return api_response(meeting_schema.dump(m), "updated")
