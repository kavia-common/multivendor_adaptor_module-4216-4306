from flask import Blueprint, jsonify
from .auth import require_auth, require_permissions
from .models import User, Role, Session, AuditLog, Version

bp = Blueprint("admin", __name__)

@bp.get("/users")
@require_auth
@require_permissions("admin:read")
def list_users():
    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "role": u.role.name if u.role else None,
        "created_at": u.created_at.isoformat()
    } for u in users])

@bp.get("/roles")
@require_auth
@require_permissions("admin:read")
def list_roles():
    roles = Role.query.all()
    return jsonify([{
        "id": r.id,
        "name": r.name,
        "permissions": [p.name for p in r.permissions],
        "created_at": r.created_at.isoformat()
    } for r in roles])

@bp.get("/sessions")
@require_auth
@require_permissions("admin:read")
def list_sessions():
    sessions = Session.query.all()
    return jsonify([{
        "id": s.id,
        "user_id": s.user_id,
        "token": s.token,
        "created_at": s.created_at.isoformat(),
        "expires_at": s.expires_at.isoformat(),
    } for s in sessions])

@bp.get("/audit_logs")
@require_auth
@require_permissions("admin:read")
def list_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(200).all()
    return jsonify([{
        "id": a.id,
        "action": a.action,
        "user_id": a.user_id,
        "timestamp": a.timestamp.isoformat(),
        "details": a.details
    } for a in logs])

@bp.get("/versions")
@require_auth
@require_permissions("admin:read")
def list_versions():
    versions = Version.query.order_by(Version.created_at.desc()).all()
    return jsonify([{
        "id": v.id,
        "entity_type": v.entity_type,
        "entity_id": v.entity_id,
        "version": v.version,
        "created_at": v.created_at.isoformat()
    } for v in versions])
