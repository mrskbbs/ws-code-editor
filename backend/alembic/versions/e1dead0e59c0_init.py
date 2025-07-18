"""Init

Revision ID: e1dead0e59c0
Revises: 
Create Date: 2025-07-18 20:16:45.182199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e1dead0e59c0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('user_',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False),
    sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.CheckConstraint("email::text ~ '^[\\w\\.-]+\\@[\\w-]+\\.[\\w-]{2,4}$'::text", name='email_regex_check'),
    sa.CheckConstraint("username::text ~ '^[a-zA-Z0-9_]+$'::text", name='username_regex_check'),
    sa.PrimaryKeyConstraint('id', name='user__pkey'),
    sa.UniqueConstraint('email', name='user__email_key'),
    sa.UniqueConstraint('username', name='user__username_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('room',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('invite_token', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('creator_id_fk', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('code', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('stdin', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['creator_id_fk'], ['user_.id'], name=op.f('room_creator_id_fk_fkey'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('room_pkey')),
    sa.UniqueConstraint('invite_token', name=op.f('room_invite_token_key'))
    )
    op.create_table('session',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False),
    sa.Column('user_id_fk', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('auth_token', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('user_agent', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id_fk'], ['user_.id'], name=op.f('session_user_id_fk_fkey'), onupdate='SET NULL', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('session_pkey')),
    sa.UniqueConstraint('auth_token', name=op.f('session_auth_token_key'))
    )
    op.create_table('association_room_user',
    sa.Column('user_id_fk', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('room_id_fk', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['room_id_fk'], ['room.id'], name=op.f('association_room_user_room_id_fk_fkey'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id_fk'], ['user_.id'], name=op.f('association_room_user_user_id_fk_fkey'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id_fk', 'room_id_fk', name=op.f('association_room_user_pkey'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE session CASCADE")
    op.execute("DROP TABLE room CASCADE")
    op.execute("DROP TABLE user_ CASCADE")
    op.execute("DROP TABLE association_room_user CASCADE")