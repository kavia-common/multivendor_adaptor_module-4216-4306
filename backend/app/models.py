from datetime import datetime, timedelta
import uuid
from sqlalchemy.dialects.postgresql import JSONB
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permission", db.String(128), primary_key=True),
)

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# PUBLIC_INTERFACE
class Role(db.Model, TimestampMixin):
    """Role with permissions for RBAC."""
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    # simple array table via association
    permissions = db.relationship(
        "Permission",
        cascade="all, delete-orphan",
        backref="role",
        lazy="dynamic",
    )

# PUBLIC_INTERFACE
class Permission(db.Model):
    """Permission row holding a single permission string for a role."""
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    name = db.Column(db.String(128), nullable=False)

# PUBLIC_INTERFACE
class User(db.Model, TimestampMixin):
    """User account with password hash and role."""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True)
    role = db.relationship("Role", backref="users")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

# PUBLIC_INTERFACE
class Session(db.Model, TimestampMixin):
    """Session token stored in DB for auth. TTL set via expires_at."""
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    user = db.relationship("User", backref="sessions")

    @staticmethod
    def new_token():
        return uuid.uuid4().hex

    @staticmethod
    def with_ttl(user_id: int, ttl_seconds: int):
        token = Session.new_token()
        now = datetime.utcnow()
        sess = Session(
            user_id=user_id, token=token, created_at=now, expires_at=now + timedelta(seconds=ttl_seconds)
        )
        return sess

# PUBLIC_INTERFACE
class Model(db.Model, TimestampMixin):
    """Stores NB or SB models."""
    __tablename__ = "models"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(8), nullable=False)  # NB or SB
    name = db.Column(db.String(128), nullable=False)
    data = db.Column(JSONB, nullable=False)
    version = db.Column(db.String(64), default="v1", nullable=False)

# PUBLIC_INTERFACE
class Mapping(db.Model, TimestampMixin):
    """Mapping between NB and SB models with mapping_data JSON."""
    __tablename__ = "mappings"
    id = db.Column(db.Integer, primary_key=True)
    nb_model_id = db.Column(db.Integer, db.ForeignKey("models.id"), nullable=False)
    sb_model_id = db.Column(db.Integer, db.ForeignKey("models.id"), nullable=False)
    mapping_data = db.Column(JSONB, nullable=False)

    nb_model = db.relationship("Model", foreign_keys=[nb_model_id])
    sb_model = db.relationship("Model", foreign_keys=[sb_model_id])

# PUBLIC_INTERFACE
class AuditLog(db.Model):
    """Audit logs for actions."""
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    details = db.Column(JSONB, nullable=True)
    user = db.relationship("User")

# PUBLIC_INTERFACE
class Version(db.Model, TimestampMixin):
    """Version tracking for entities."""
    __tablename__ = "versions"
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(64), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    version = db.Column(db.String(64), default="v1", nullable=False)
