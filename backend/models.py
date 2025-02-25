import uuid
from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from db import db


def generate_uuid():
    return str(uuid.uuid4())


# User Model
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


# Association table for chat participants (Many-to-Many)
chat_participants = db.Table(
    "chat_participants",
    db.Column("chat_id", db.String(36), db.ForeignKey("chats.id"), primary_key=True),
    db.Column("user_id", db.String(36), db.ForeignKey("users.id"), primary_key=True),
)


# Message Model
class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    chat_id = db.Column(db.String(36), db.ForeignKey("chats.id"), nullable=False)
    sender_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(tz=timezone.utc))

    sender = db.relationship("User", backref="messages")

    def __init__(self, chat_id, sender_id, text):
        self.chat_id = chat_id
        self.sender_id = sender_id
        self.text = text

    def __repr__(self):
        return f"<Message {self.id} from {self.sender_id}>"


# Chat Model (Represents a conversation)
class Chat(db.Model):
    __tablename__ = "chats"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    created_at = db.Column(db.DateTime, default=datetime.now(tz=timezone.utc))
    participants = db.relationship("User", secondary=chat_participants, backref="chats")
    last_message_id = db.Column(
        db.String(36), db.ForeignKey("messages.id"), nullable=True
    )
    last_message = db.relationship(
        "Message", foreign_keys=[last_message_id], uselist=False
    )

    def __init__(self):
        self.participants = []

    def __repr__(self):
        return f"<Chat {self.id}>"
