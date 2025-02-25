"""Create messages table and add foreign keys

Revision ID: b37c2d5f54f4
Revises: 253e505793b9
Create Date: 2025-02-23 20:09:29.466801

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b37c2d5f54f4"
down_revision: Union[str, None] = "253e505793b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("chat_id", sa.String(36), nullable=False),
        sa.Column("sender_id", sa.String(36), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"]),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Add the foreign key constraint from chats to messages
    op.add_column("chats", sa.Column("last_message_id", sa.String(36), nullable=True))
    op.create_foreign_key(
        "fk_last_message", "chats", "messages", ["last_message_id"], ["id"]
    )


def downgrade():
    # Drop constraints and tables in reverse order
    op.drop_constraint("fk_last_message", "chats", type_="foreignkey")
    op.drop_column("chats", "last_message_id")
    op.drop_table("messages")
