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

ALLOWED_EXTS = {"pdf", "ppt", "pptx", "doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg", "zip", "txt"}

def _allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

@resources_bp.post("")
@jwt_required()
def upload_resource():
    if current_user_role() != "professor":
        return api_response(None, "only professors can upload", 403)

    year = (request.form.get("year") or "").strip()
    branch = (request.form.get("branch") or "").strip()
    subject = (request.form.get("subject") or "").strip()
    section = (request.form.get("section") or "").strip()
    file = request.files.get("file")

    if not year or not branch or not subject or not section or not file:
        return api_response(None, "year, branch, subject, section and file are required", 400)

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
        uploader_id=current_user_id(),
        year=year,
        branch=branch,
        subject=subject,
        section=section,
        filename=fname,
        url=f"/api/resources/file/{new_name}"
    )

    db.session.add(res)
    db.session.commit()
    return api_response(resource_schema.dump(res), "uploaded", 201)

@resources_bp.get("")
def list_resources():
    year = (request.args.get("year") or "").strip()
    branch = (request.args.get("branch") or "").strip()
    subject = (request.args.get("subject") or "").strip()
    section = (request.args.get("section") or "").strip()

    qs = Resource.query

    if year:
        qs = qs.filter(Resource.year.ilike(f"%{year}%"))
    if branch:
        qs = qs.filter(Resource.branch.ilike(f"%{branch}%"))
    if subject:
        qs = qs.filter(Resource.subject.ilike(f"%{subject}%"))
    if section:
        qs = qs.filter(Resource.section.ilike(f"%{section}%"))

    resources = qs.order_by(Resource.created_at.desc()).all()
    return api_response(resources_schema.dump(resources))

@resources_bp.get("/file/<string:stored>")
def serve_file(stored):
    upload_dir = os.path.join(current_app.root_path, "uploads")
    return current_app.send_from_directory(upload_dir, stored, as_attachment=False)