from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import Meeting
from ..schemas import meeting_schema, meetings_schema
from ..utils import api_response, current_user_id, current_user_role

meetings_bp = Blueprint("meetings", __name__, url_prefix="/api/meetings")


def is_professor_for_meeting(meeting):
    role = (current_user_role() or "").strip().lower()
    uid = current_user_id()

    if role != "professor":
        return False, "only professors can perform this action"

    if meeting.professor_id != uid:
        return False, "this meeting does not belong to the logged-in professor"

    return True, ""


@meetings_bp.post("")
@jwt_required()
def create_meeting():
    role = (current_user_role() or "").strip().lower()

    if role != "student":
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
            update_note="Meeting requested by Student",
            last_updated_by="student",
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
    role = (current_user_role() or "").strip().lower()

    if role != "professor":
        return api_response(None, "only professors", 403)

    ms = (
        Meeting.query
        .filter_by(professor_id=current_user_id())
        .order_by(Meeting.created_at.desc())
        .all()
    )
    return api_response(meetings_schema.dump(ms))

@meetings_bp.get("")
@jwt_required()
def list_meetings():
    role = current_user_role()
    uid = current_user_id()

    qs = Meeting.query

    if role == "professor":
        qs = qs.filter(Meeting.professor_id == uid)

    if role == "student":
        qs = qs.filter(Meeting.student_id == uid)

    return api_response(meetings_schema.dump(qs.all()))

@meetings_bp.get("/mine")
@jwt_required()
def my_meetings():
    role = (current_user_role() or "").strip().lower()
    uid = current_user_id()

    if role == "student":
        query = Meeting.query.filter_by(student_id=uid)
    elif role == "professor":
        query = Meeting.query.filter_by(professor_id=uid)
    else:
        return api_response(None, "invalid user role", 403)

    ms = query.order_by(Meeting.date.desc(), Meeting.start_time.desc()).all()
    return api_response(meetings_schema.dump(ms))


@meetings_bp.post("/<int:meeting_id>/accept")
@jwt_required()
def accept_meeting(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)

    allowed, message = is_professor_for_meeting(m)
    if not allowed:
        return api_response(None, message, 403)

    m.status = "confirmed"
    m.last_updated_by = "professor"
    m.update_note = "Meeting accepted by Professor"

    db.session.commit()
    return api_response(meeting_schema.dump(m), "accepted")


@meetings_bp.post("/<int:meeting_id>/reject")
@jwt_required()
def reject_meeting(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)

    allowed, message = is_professor_for_meeting(m)
    if not allowed:
        return api_response(None, message, 403)

    m.status = "rejected"
    m.last_updated_by = "professor"
    m.update_note = "Meeting rejected by Professor"

    db.session.commit()
    return api_response(meeting_schema.dump(m), "rejected")


@meetings_bp.post("/<int:meeting_id>/reschedule")
@jwt_required()
def reschedule(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)

    allowed, message = is_professor_for_meeting(m)
    if not allowed:
        return api_response(None, message, 403)

    payload = request.get_json() or {}

    try:
        schedule_changed = False
        location_changed = False

        if payload.get("date"):
            m.date = datetime.strptime(payload["date"], "%Y-%m-%d").date()
            schedule_changed = True

        if payload.get("start_time"):
            m.start_time = datetime.strptime(payload["start_time"], "%H:%M").time()
            schedule_changed = True

        if payload.get("end_time"):
            m.end_time = datetime.strptime(payload["end_time"], "%H:%M").time()
            schedule_changed = True

        if payload.get("location"):
            m.location = payload["location"].strip()
            location_changed = True

    except Exception:
        return api_response(None, "bad date/time format", 400)

    # keep meeting active/confirmed after professor edits
    if m.status != "rejected":
        m.status = "confirmed"

    m.last_updated_by = "professor"

    if schedule_changed and location_changed:
        m.update_note = "Meeting rescheduled and location changed by Professor"
    elif schedule_changed:
        m.update_note = "Meeting rescheduled by Professor"
    elif location_changed:
        m.update_note = "Meeting location changed by Professor"
    else:
        m.update_note = "Meeting updated by Professor"

    db.session.commit()
    return api_response(meeting_schema.dump(m), "updated")