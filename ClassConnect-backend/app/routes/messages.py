from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import Message
from ..schemas import message_schema, messages_schema
from ..utils import api_response, current_user_id

messages_bp = Blueprint("messages", __name__, url_prefix="/api/messages")

@messages_bp.post("")
@jwt_required()
def send_message():
    payload = request.get_json() or {}
    msg = Message(
        sender_id=current_user_id(),
        recipient_id=int(payload.get("recipient_id")),
        body=(payload.get("body") or "").strip(),
        meeting_id=payload.get("meeting_id"),
    )
    if not msg.body:
        return api_response(None, "body is required", 400)
    db.session.add(msg)
    db.session.commit()
    return api_response(message_schema.dump(msg), "sent", 201)

@messages_bp.get("/thread")
@jwt_required()
def get_thread():
    try:
        other_id = int(request.args.get("with_user_id"))
    except Exception:
        return api_response(None, "with_user_id required", 400)
    uid = current_user_id()
    qs = Message.query.filter(
        ((Message.sender_id == uid) & (Message.recipient_id == other_id)) |
        ((Message.sender_id == other_id) & (Message.recipient_id == uid))
    ).order_by(Message.created_at.asc()).all()
    return api_response(messages_schema.dump(qs))
