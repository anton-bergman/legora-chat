from typing import Optional, List
from models import User, Chat, Message
from db import db


def get_user_by_username(username: str) -> User | None:
    """
    Retrieve a user by their username.
    """
    return db.session.query(User).filter_by(username=username).first()


def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Retrieve a user from the database by user ID.
    Returns the User object if found, or None if no user is found.
    """
    return User.query.get(user_id)


def get_chat_by_id(chat_id: str) -> Optional[Chat]:
    """
    Retrieve a chat from the database by chat ID.
    Returns the Chat object if found, or None if no chat is found.
    """
    return Chat.query.get(chat_id)


def get_messages_by_chat_id(chat_id: str) -> List[Message]:
    """
    Retrieve all messages for a given chat ID.
    Returns a list of Message objects.
    """
    return Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()


def get_chats_by_user_id(user_id: str) -> List[Chat]:
    """
    Retrieve all chats that a given user is a participant in.
    Returns a list of Chat objects.
    """
    return Chat.query.filter(Chat.participants.any(id=user_id)).all()


def create_chat(participants: List[User]) -> Chat:
    """
    Create a new chat with the given participants.
    Returns the created Chat object.
    """
    new_chat = Chat()
    new_chat.participants.extend(participants)
    db.session.add(new_chat)
    db.session.commit()
    return new_chat


def create_message(chat_id: str, sender_id: str, text: str) -> Message:
    """
    Create a new message to a chat.
    Updates the chat's last_message_id.
    Returns the created Message object.
    """
    new_message = Message(chat_id=chat_id, sender_id=sender_id, text=text)
    db.session.add(new_message)

    chat = get_chat_by_id(chat_id)
    if chat:
        chat.last_message_id = new_message.id

    db.session.commit()
    return new_message


def check_chat_exists(user1_id: str, user2_id: str) -> Optional[Chat]:
    """
    Check if two users have a chat.
    """
    chat = Chat.query.filter(
        Chat.participants.any(id=user1_id), Chat.participants.any(id=user2_id)
    ).first()

    return chat
