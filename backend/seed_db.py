from app import create_app, db
from models import Chat, Message, User, chat_participants


def reset_database():
    db.session.execute(chat_participants.delete())  # Clear association table first
    db.session.query(Message).delete()
    db.session.query(Chat).delete()
    db.session.query(User).delete()
    db.session.commit()
    print("Database reset completed.")


# Create mock users
def create_mock_users():
    users_dict = {
        "anton": "password123",
        "bugge": "password123",
        "bergman": "password123",
        "alice": "password123",
        "bob": "password123",
        "charlie": "password123",
    }

    users = []
    for username, password in users_dict.items():
        user = User(username=username, password=password)
        users.append(user)

    db.session.add_all(users)
    db.session.commit()
    print("Users created.")
    return users


# Create mock chats with messages
def create_mock_chats(users):
    chat1 = Chat()
    chat2 = Chat()

    chat1.participants.extend([users[0], users[1]])  # Anton <-> Bugge
    chat2.participants.extend([users[0], users[2]])  # Anton <-> Bergman

    db.session.add_all([chat1, chat2])
    db.session.commit()
    print("Chats created.")

    return [chat1, chat2]


# Create mock messages
def create_mock_messages(chats, users):
    messages = [
        Message(
            chat_id=chats[0].id,
            sender_id=users[0].id,
            text="Hey Bugge, how's it going?",
        ),
        Message(
            chat_id=chats[0].id, sender_id=users[1].id, text="Hey Anton! Doing great."
        ),
        Message(
            chat_id=chats[1].id,
            sender_id=users[0].id,
            text="Yo Bergman, ready for the match?",
        ),
        Message(
            chat_id=chats[1].id, sender_id=users[2].id, text="Absolutely! Let’s do it."
        ),
    ]

    db.session.add_all(messages)
    db.session.commit()
    print("Messages created.")

    # Update last message reference in chats
    for chat in chats:
        last_message = (
            Message.query.filter_by(chat_id=chat.id)
            .order_by(Message.timestamp.desc())
            .first()
        )
        chat.last_message_id = last_message.id if last_message else None

    db.session.commit()
    print("Chat last message updated.")


# Run the seeding process
def seed_database():
    reset_database()
    users = create_mock_users()
    chats = create_mock_chats(users)
    create_mock_messages(chats, users)
    print("Database seeded successfully!")


if __name__ == "__main__":
    # Initialize the Flask app
    app = create_app()

    with app.app_context():
        seed_database()
