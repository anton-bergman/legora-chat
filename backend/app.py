from datetime import datetime
from typing import List, Optional

from dateutil import parser
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    decode_token,
    get_jwt_identity,
    jwt_required,
)
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit, join_room
from pydantic import BaseModel, ValidationError, field_validator
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

import queries
from db import db
from models import Chat, Message, User, chat_participants

migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()


def create_app():
    app = Flask(__name__)

    # PostgreSQL database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://admin:password@localhost/legora_chat_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "legora_chat"

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    return app


app = create_app()

# Enable CORS for frontend requests
CORS(app)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    token: str


class LastMessageResponse(BaseModel):
    sender: Optional[str] = None
    text: Optional[str] = None
    timestamp: Optional[datetime] = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        if isinstance(value, str):
            return parser.parse(value)
        elif isinstance(value, datetime):
            return value
        return None


class ChatResponse(BaseModel):
    chatId: str
    participants: List[str]
    lastMessage: Optional[LastMessageResponse] = None


class MessageResponse(BaseModel):
    messageId: str
    chatId: str
    sender: str
    text: str
    timestamp: datetime

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        if isinstance(value, str):
            return parser.parse(value)
        elif isinstance(value, datetime):
            return value
        else:
            raise ValueError(f"Invalid timestamp format: {value}")


class ChatMessagesResponse(BaseModel):
    chatId: str
    messages: List[MessageResponse]


class SendMessageRequest(BaseModel):
    chat_id: str
    text: str


class CreateChatRequest(BaseModel):
    participant_username: str


class CreateChatResponse(BaseModel):
    chatId: str
    participants: List[str]


@socketio.on("connect")
def handle_connect():
    """Handles WebSocket connection."""
    try:
        token = request.args.get("token")
        if not token:
            emit("error", {"message": "Authentication token is required"})
            return

        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")
        if not user_id:
            emit("error", {"message": "Invalid authentication token"})
            return

        join_room(user_id)
        emit("connected", {"message": "Connected to WebSocket server"})
    except Exception:
        emit("error", {"message": "Authentication failed"})


@socketio.on("send_message")
def handle_message(data):
    """Handles sending a message to a chat."""
    try:
        if not isinstance(data, dict):
            emit("error", {"message": "Invalid data format"})
            return

        token = request.args.get("token")
        if not token:
            emit("error", {"message": "Authentication token required"})
            return

        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")
        if not user_id:
            emit("error", {"message": "Invalid authentication token"})
            return

        data = MessageResponse(**data)
        emit(
            "new_message",
            {
                "chatId": data.chatId,
                "messageId": data.messageId,
                "sender": data.sender,
                "text": data.text,
                "timestamp": data.timestamp.isoformat(),
            },
            room=data.chatId,
        )
    except ValidationError as e:
        emit("error", {"message": e.errors()})
    except Exception:
        emit("error", {"message": "Failed to send message"})


@socketio.on("join_chat")
def handle_join_chat(data):
    """Handles user joining a chat room."""
    try:
        print("data: ", data)
        if not isinstance(data, dict):
            emit("error", {"message": "Invalid data format"})
            return

        token = request.args.get("token")
        if not token:
            emit("error", {"message": "Authentication token required"})
            return

        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")
        if not user_id:
            emit("error", {"message": "Invalid authentication token"})
            return

        data = ChatResponse(**data)
        chat = queries.get_chat_by_id(data.chatId)
        if not chat:
            emit("error", {"message": "Chat not found"})
            return

        join_room(chat.id)
        emit("chat_joined", {"message": f"Joined chat {chat.id}"}, room=chat.id)
    except ValidationError as e:
        emit("error", {"message": e.errors()})
    except Exception:
        emit("error", {"message": "Failed to join chat"})


@socketio.on("new_chat")
def handle_new_chat(data):
    """Handles notification for new chat creation."""
    try:
        if not isinstance(data, dict):
            emit("error", {"message": "Invalid data format"})
            return

        token = request.args.get("token")
        if not token:
            emit("error", {"message": "Authentication token required"})
            return

        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")
        if not user_id:
            emit("error", {"message": "Invalid authentication token"})
            return

        user = queries.get_user_by_id(user_id)
        data = CreateChatResponse(**data)
        other_users = [
            username for username in data.participants if username != user.username
        ]
        other_user = queries.get_user_by_username(other_users[0])
        emit(
            "new_chat",
            {
                "chatId": data.chatId,
                "participants": data.participants,
                "lastMessage": None,
            },
            room=other_user.id,
        )
    except ValidationError as e:
        emit("error", {"message": e.errors()})
    except Exception:
        emit("error", {"message": "Failed to notify new chat"})


@socketio.on("disconnect")
def handle_disconnect():
    """Handle disconnection event"""
    try:
        token = request.args.get("token")
        if not token:
            emit("error", {"message": "Authentication token required"})
            return

        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")
        if not user_id:
            emit("error", {"message": "Invalid authentication token"})
            return
        emit("disconnected", {"message": "Websocket server disconnected"})
    except Exception:
        emit("error", {"message": "Disconnect failed"})


@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if data is None:
            raise BadRequest("Request body cannot be empty")
        if not isinstance(data, dict):
            raise BadRequest("Request body must be a valid JSON object")

        data = LoginRequest(**data)
        user = queries.get_user_by_username(username=data.username)
        if user and user.check_password(data.password):
            access_token = create_access_token(identity=user.id)
            response = LoginResponse(username=user.username, token=access_token)
            return jsonify(response.model_dump()), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except UnsupportedMediaType as e:
        return jsonify({"error": e.description}), 415
    except BadRequest as e:
        return jsonify({"error": e.description}), 400
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400


@app.route("/api/chats", methods=["GET"])
@jwt_required()
def get_user_chats():
    """Fetch all chats for the logged-in user."""
    user_id = get_jwt_identity()
    user_chats = queries.get_chats_by_user_id(user_id)
    if user_chats is None:
        chat_list = []

    chat_list = [
        ChatResponse(
            chatId=chat.id,
            participants=[p.username for p in chat.participants],
            lastMessage=LastMessageResponse(
                sender=chat.last_message.sender.username if chat.last_message else None,
                text=chat.last_message.text if chat.last_message else None,
                timestamp=chat.last_message.timestamp if chat.last_message else None,
            )
            if chat.last_message
            else None,
        )
        for chat in user_chats
    ]
    return jsonify([chat.model_dump() for chat in chat_list]), 200


@app.route("/api/chats/<chat_id>", methods=["GET"])
@jwt_required()
def get_chat_messages(chat_id):
    """Fetch all messages in a given chat."""
    user_id = get_jwt_identity()
    chat = queries.get_chat_by_id(chat_id)

    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    if user_id not in [p.id for p in chat.participants]:
        return jsonify({"error": "Access denied"}), 404

    messages = queries.get_messages_by_chat_id(chat_id)
    response = ChatMessagesResponse(
        chatId=chat.id,
        messages=[
            MessageResponse(
                messageId=msg.id,
                chatId=msg.chat_id,
                sender=msg.sender.username,
                text=msg.text,
                timestamp=msg.timestamp,
            )
            for msg in messages
        ],
    )
    return jsonify(response.model_dump()), 200


@app.route("/api/messages", methods=["POST"])
@jwt_required()
def send_message():
    """Send a message in a chat."""
    try:
        data = request.get_json()
        if data is None:
            raise BadRequest("Request body cannot be empty")
        if not isinstance(data, dict):
            raise BadRequest("Request body must be a valid JSON object")

        data = SendMessageRequest(**data)
        user_id = get_jwt_identity()
        chat = queries.get_chat_by_id(data.chat_id)

        if not chat:
            return jsonify({"error": "Chat not found"}), 404

        if user_id not in [p.id for p in chat.participants]:
            return jsonify({"error": "Access denied"}), 404

        new_message = queries.create_message(
            chat_id=data.chat_id, sender_id=user_id, text=data.text
        )
        response = MessageResponse(
            messageId=new_message.id,
            chatId=new_message.chat_id,
            sender=new_message.sender.username,
            text=new_message.text,
            timestamp=new_message.timestamp,
        )
        return jsonify(response.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400


@app.route("/api/chats", methods=["POST"])
@jwt_required()
def create_chat():
    """Create a new chat with another user."""
    try:
        data = request.get_json()
        if data is None:
            raise BadRequest("Request body cannot be empty")
        if not isinstance(data, dict):
            raise BadRequest("Request body must be a valid JSON object")

        data = CreateChatRequest(**data)
        user_id = get_jwt_identity()
        user = queries.get_user_by_id(user_id)
        other_user = queries.get_user_by_username(data.participant_username)

        if user == other_user or not user or not other_user:
            return jsonify({"error": "User not found"}), 404

        existing_chat = queries.check_chat_exists(user_id, other_user.id)
        if existing_chat:
            return jsonify({"error": "Chat already exists"}), 400

        participants: List[User] = [user, other_user]
        new_chat = queries.create_chat(participants)

        participant_names = [user.username, other_user.username]
        response = CreateChatResponse(
            chatId=new_chat.id, participants=participant_names
        )
        return jsonify(response.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400


@app.route("/api/verify", methods=["GET"])
@jwt_required()
def verify_token():
    """Verify if JWT is valid and return user identity"""
    try:
        user_id = get_jwt_identity()
        return jsonify({"message": "Token is valid", "user_id": user_id}), 200
    except Exception:
        return jsonify({"error": "Invalid or expired token"}), 401


if __name__ == "__main__":
    # app.run(debug=True, port=5000)
    socketio.run(app, debug=True, port=5000)
