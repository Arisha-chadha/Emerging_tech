from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    name = fields.Str(required=True)
    role = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class ProfessorSchema(Schema):
    user = fields.Nested(UserSchema)
    department = fields.Str()
    cabin_location = fields.Str()

class AvailabilitySlotSchema(Schema):
    id = fields.Int(dump_only=True)
    professor_id = fields.Int(required=True)
    date = fields.Date(required=True)
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)
    location = fields.Str(required=True)
    is_active = fields.Bool()

class MeetingSchema(Schema):
    id = fields.Int(dump_only=True)
    student = fields.Nested(UserSchema, dump_only=True)
    professor = fields.Nested(UserSchema, dump_only=True)
    student_id = fields.Int(load_only=True)
    professor_id = fields.Int(load_only=True)
    date = fields.Date(required=True)
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)
    location = fields.Str(required=True)
    agenda = fields.Str()
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)

    update_note = fields.Str(allow_none=True)
    last_updated_by = fields.Str(allow_none=True)

class MessageSchema(Schema):
    id = fields.Int(dump_only=True)
    sender = fields.Nested(UserSchema, dump_only=True)
    recipient = fields.Nested(UserSchema, dump_only=True)
    sender_id = fields.Int(load_only=True)
    recipient_id = fields.Int(load_only=True)
    body = fields.Str(required=True)
    meeting_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)

class ResourceSchema(Schema):
    id = fields.Int(dump_only=True)
    uploader = fields.Nested(UserSchema, dump_only=True)

    year = fields.Str(required=True)
    branch = fields.Str(required=True)
    subject = fields.Str(required=True)
    section = fields.Str(required=True)

    filename = fields.Str(dump_only=True)
    url = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

user_schema = UserSchema()
availability_schema = AvailabilitySlotSchema()
availability_list_schema = AvailabilitySlotSchema(many=True)
meeting_schema = MeetingSchema()
meetings_schema = MeetingSchema(many=True)
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)
resource_schema = ResourceSchema()
resources_schema = ResourceSchema(many=True)