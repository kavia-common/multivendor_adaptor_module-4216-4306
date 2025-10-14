import os
from functools import wraps
from datetime import datetime
from flask import request, jsonify, g
from . import db
from .models import User, Session, Role, Permission, AuditLog

TOKEN_HEADER = "X-Session-Token"

def _error(code, message, details=None, http_status=401):
    return jsonify({"code": code, "message": message, "details": details or {}}), http_status

# PUBLIC_INTERFACE
def require_auth(f):
    """Decorator to require a valid session token."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get(TOKEN_HEADER) or request.cookies.get("session_token")
        if not token:
            return _error("auth_missing", "Missing session token", http_status=401)
        session = Session.query.filter_by(token=token).first()
        if not session:
            return _error("auth_invalid", "Invalid session token", http_status=401)
        if session.expires_at < datetime.utcnow():
            db.session.delete(session)
            db.session.commit()
            return _error("auth_expired", "Session expired", http_status=401)
        g.current_user = session.user
        g.current_session = session
        return f(*args, **kwargs)
    return wrapper

# PUBLIC_INTERFACE
def require_permissions(*required_permissions):
    """Decorator to require RBAC permissions. If user role is 'admin', always allowed."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not getattr(g, "current_user", None):
                return _error("auth_missing", "Not authenticated", http_status=401)
            user: User = g.current_user
            if user.role and user.role.name == "admin":
                return f(*args, **kwargs)
            if not user.role:
                return _error("forbidden", "Role not assigned", http_status=403)
            role: Role = user.role
            perms = set(p.name for p in role.permissions)
            if not set(required_permissions).issubset(perms):
                return _error("forbidden", "Insufficient permissions", {"required": required_permissions}, http_status=403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

# PUBLIC_INTERFACE
def audit(action: str, user_id: int | None, details: dict | None = None):
    """Create an audit log entry."""
    log = AuditLog(action=action, user_id=user_id, details=details or {})
    db.session.add(log)
    db.session.commit()
    return log
