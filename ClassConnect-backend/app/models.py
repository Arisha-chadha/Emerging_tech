from datetime import datetime
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(TimestampMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="student")  # 'student' or 'professor'

    def set_password(self, raw: str):
        self.password_hash = generate_password_hash(raw, method="pbkdf2:sha256")

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

class ProfessorProfile(TimestampMixin, db.Model):
    __tablename__ = "professor_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    department = db.Column(db.String(120))
    cabin_location = db.Column(db.String(120))
    user = db.relationship("User", backref=db.backref("professor_profile", uselist=False))

class AvailabilitySlot(TimestampMixin, db.Model):
    __tablename__ = "availability_slots"
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    professor = db.relationship("User", backref=db.backref("availability", lazy=True))

class Meeting(TimestampMixin, db.Model):
    __tablename__ = "meetings"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    agenda = db.Column(db.String(255), default="")
    status = db.Column(db.String(20), default="pending")  # pending/confirmed/rejected/cancelled

    student = db.relationship("User", foreign_keys=[student_id])
    professor = db.relationship("User", foreign_keys=[professor_id])

class Message(TimestampMixin, db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.id"), nullable=True)

    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])
    meeting = db.relationship("Meeting", backref=db.backref("messages", lazy=True))

class Resource(TimestampMixin, db.Model):
    __tablename__ = "resources"
    id = db.Column(db.Integer, primary_key=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    course = db.Column(db.String(120), nullable=True)
    semester = db.Column(db.String(50), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)

    uploader = db.relationship("User", backref=db.backref("resources", lazy=True))
