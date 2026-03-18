from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import AvailabilitySlot
from ..schemas import availability_schema, availability_list_schema
from ..utils import api_response, current_user_id, current_user_role

availability_bp = Blueprint("availability", __name__, url_prefix="/api/availability")

@availability_bp.get("")
def list_public():
    qdate = request.args.get("date")
    query = AvailabilitySlot.query.filter_by(is_active=True)
    if qdate:
        try:
            d = datetime.strptime(qdate, "%Y-%m-%d").date()
            query = query.filter(AvailabilitySlot.date == d)
        except Exception:
            return api_response(None, "invalid date format", 400)
    slots = query.order_by(AvailabilitySlot.date, AvailabilitySlot.start_time).all()
    return api_response(availability_list_schema.dump(slots))

@availability_bp.post("")
@jwt_required()
def add_slot():
    if current_user_role() != "professor":
        return api_response(None, "only professors can add availability", 403)

    payload = request.get_json() or {}
    try:
        slot = AvailabilitySlot(
            professor_id=current_user_id(),
            date=datetime.strptime(payload["date"], "%Y-%m-%d").date(),
            start_time=datetime.strptime(payload["start_time"], "%H:%M").time(),
            end_time=datetime.strptime(payload["end_time"], "%H:%M").time(),
            location=payload.get("location", "TBD"),
            is_active=True,
        )
    except KeyError as e:
        return api_response(None, f"missing field {e}", 400)
    except Exception:
        return api_response(None, "bad date/time format", 400)

    db.session.add(slot)
    db.session.commit()
    return api_response(availability_schema.dump(slot), "created", 201)

@availability_bp.delete("/<int:slot_id>")
@jwt_required()
def delete_slot(slot_id):
    slot = AvailabilitySlot.query.get_or_404(slot_id)
    if slot.professor_id != current_user_id():
        return api_response(None, "not your slot", 403)
    db.session.delete(slot)
    db.session.commit()
    return api_response({}, "deleted")
