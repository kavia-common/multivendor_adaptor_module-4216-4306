from datetime import datetime
import os
from flask import Blueprint, request, jsonify, g, make_response
from . import db
from .models import User, Session
from .errors import error_response
from .auth import require_auth, audit

bp = Blueprint("auth", __name__)

@bp.post("/login")
def login():
    """Login with username and password, returns session token."""
    data = request.get_json(silent=True) or {}
    missing = [k for k in ["username", "password"] if k not in data or not data[k]]
    if missing:
        return error_response("invalid_input", "Missing fields", {"missing": missing}, 400)
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return error_response("auth_failed", "Invalid credentials", status=401)
    ttl = int(os.getenv("SESSION_TOKEN_TTL_SECONDS", "86400"))
    session = Session.with_ttl(user.id, ttl)
    db.session.add(session)
    db.session.commit()
    audit("login", user.id, {"username": user.username, "session": session.token})
    resp = jsonify({"token": session.token, "user": {"id": user.id, "username": user.username, "role": user.role.name if user.role else None}})
    # Also set cookie for convenience
    r = make_response(resp)
    expires = session.expires_at
    r.set_cookie("session_token", session.token, httponly=True, samesite="Lax", expires=expires)
    return r, 200

@bp.post("/logout")
@require_auth
def logout():
    """Logout current session."""
    sess: Session = g.current_session
    user = g.current_user
    db.session.delete(sess)
    db.session.commit()
    audit("logout", user.id if user else None, {"session": sess.token})
    r = jsonify({"message": "Logged out"})
    resp = make_response(r)
    resp.delete_cookie("session_token")
    return resp, 200
