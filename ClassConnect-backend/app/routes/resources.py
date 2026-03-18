import os
from uuid import uuid4
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import Resource
from ..schemas import resource_schema, resources_schema
from ..utils import api_response, current_user_id, current_user_role

resources_bp = Blueprint("resources", __name__, url_prefix="/api/resources")

ALLOWED_EXTS = {"pdf","ppt","pptx","doc","docx","xls","xlsx","png","jpg","jpeg","zip","txt"}

def _allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

@resources_bp.post("")
@jwt_required()
def upload_resource():
    if current_user_role() != "professor":
        return api_response(None, "only professors can upload", 403)
    subject = request.form.get("subject")
    course = request.form.get("course")
    semester = request.form.get("semester")
    file = request.files.get("file")
    if not file or not subject:
        return api_response(None, "subject and file required", 400)
    if not _allowed(file.filename):
        return api_response(None, "file type not allowed", 400)

    fname = secure_filename(file.filename)
    ext = fname.rsplit(".", 1)[-1]
    new_name = f"{uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.root_path, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, new_name)
    file.save(path)

    res = Resource(
        uploader_id=current_user_id(), subject=subject, course=course, semester=semester,
        filename=fname, url=f"/api/resources/file/{new_name}"
    )
    db.session.add(res)
    db.session.commit()
    return api_response(resource_schema.dump(res), "uploaded", 201)

@resources_bp.get("")
def list_resources():
    subject = request.args.get("subject")
    course = request.args.get("course")
    semester = request.args.get("semester")
    qs = Resource.query
    if subject:
        qs = qs.filter(Resource.subject.ilike(f"%{subject}%"))
    if course:
        qs = qs.filter(Resource.course.ilike(f"%{course}%"))
    if semester:
        qs = qs.filter(Resource.semester.ilike(f"%{semester}%"))
    return api_response(resources_schema.dump(qs.order_by(Resource.created_at.desc()).all()))

@resources_bp.get("/file/<string:stored>")
def serve_file(stored):
    upload_dir = os.path.join(current_app.root_path, "uploads")
    return current_app.send_from_directory(upload_dir, stored, as_attachment=False)
