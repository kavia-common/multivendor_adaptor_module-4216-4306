"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-10-14 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime
from werkzeug.security import generate_password_hash

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    op.create_table('models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('type', sa.String(length=8), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('version', sa.String(length=64), nullable=False, server_default='v1'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('nb_model_id', sa.Integer(), nullable=False),
        sa.Column('sb_model_id', sa.Integer(), nullable=False),
        sa.Column('mapping_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['nb_model_id'], ['models.id'], ),
        sa.ForeignKeyConstraint(['sb_model_id'], ['models.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=128), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=64), nullable=False, server_default='v1'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sessions_token', 'sessions', ['token'], unique=True)

    # Seed roles and permissions
    conn = op.get_bind()
    # admin role
    conn.execute(sa.text("INSERT INTO roles (id, created_at, name) VALUES (:id, :created_at, :name)"),
                 {"id": 1, "created_at": datetime.utcnow(), "name": "admin"})
    perms = [
        "models:create","models:read",
        "mappings:create","mappings:read",
        "provision:execute",
        "admin:read"
    ]
    for p in perms:
        conn.execute(sa.text("INSERT INTO permissions (role_id, name) VALUES (:role_id, :name)"),
                     {"role_id": 1, "name": p})
    # default admin user (password: admin123)
    pwd = generate_password_hash("admin123")
    conn.execute(sa.text("""
        INSERT INTO users (id, created_at, username, password_hash, role_id)
        VALUES (:id, :created_at, :username, :password_hash, :role_id)
    """), {"id": 1, "created_at": datetime.utcnow(), "username": "admin", "password_hash": pwd, "role_id": 1})

def downgrade():
    op.drop_index('ix_sessions_token', table_name='sessions')
    op.drop_table('sessions')
    op.drop_table('versions')
    op.drop_table('audit_logs')
    op.drop_table('mappings')
    op.drop_table('models')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
    op.drop_table('permissions')
    op.drop_table('roles')
