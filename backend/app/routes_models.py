from flask import Blueprint, request, jsonify
from . import db
from .models import Model, Version
from .errors import error_response
from .auth import require_auth, require_permissions, audit

bp = Blueprint("models", __name__)

@bp.post("/models")
@require_auth
@require_permissions("models:create")
def create_model():
    """Create NB or SB model."""
    data = request.get_json(silent=True) or {}
    missing = [k for k in ["type", "name", "data"] if k not in data]
    if missing:
        return error_response("invalid_input", "Missing fields", {"missing": missing}, 400)
    if data["type"] not in ("NB", "SB"):
        return error_response("invalid_input", "type must be NB or SB", status=400)
    version = data.get("version", "v1")
    model = Model(type=data["type"], name=data["name"], data=data["data"], version=version)
    db.session.add(model)
    db.session.commit()
    ver = Version(entity_type="Model", entity_id=model.id, version=version)
    db.session.add(ver)
    db.session.commit()
    audit("model_create", getattr(getattr(request, "user", None), "id", None), {"model_id": model.id, "type": model.type})
    return jsonify({"id": model.id, "type": model.type, "name": model.name, "version": model.version, "created_at": model.created_at.isoformat()}), 201

@bp.get("/models")
@require_auth
@require_permissions("models:read")
def list_models():
    """List models."""
    items = Model.query.order_by(Model.created_at.desc()).all()
    return jsonify([{
        "id": m.id, "type": m.type, "name": m.name, "version": m.version, "created_at": m.created_at.isoformat()
    } for m in items]), 200
