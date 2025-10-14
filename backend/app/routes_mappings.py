from flask import Blueprint, request, jsonify
from . import db
from .models import Mapping, Model, Version
from .errors import error_response
from .auth import require_auth, require_permissions, audit

bp = Blueprint("mappings", __name__)

@bp.post("/mappings")
@require_auth
@require_permissions("mappings:create")
def create_mapping():
    """Create mapping between NB and SB model."""
    data = request.get_json(silent=True) or {}
    missing = [k for k in ["nb_model_id", "sb_model_id", "mapping_data"] if k not in data]
    if missing:
        return error_response("invalid_input", "Missing fields", {"missing": missing}, 400)
    nb = Model.query.get(data["nb_model_id"])
    sb = Model.query.get(data["sb_model_id"])
    if not nb or nb.type != "NB":
        return error_response("invalid_input", "nb_model_id invalid", status=400)
    if not sb or sb.type != "SB":
        return error_response("invalid_input", "sb_model_id invalid", status=400)
    mapping = Mapping(nb_model_id=nb.id, sb_model_id=sb.id, mapping_data=data["mapping_data"])
    db.session.add(mapping)
    db.session.commit()
    ver = Version(entity_type="Mapping", entity_id=mapping.id, version="v1")
    db.session.add(ver)
    db.session.commit()
    audit("mapping_create", None, {"mapping_id": mapping.id})
    return jsonify({"id": mapping.id, "nb_model_id": mapping.nb_model_id, "sb_model_id": mapping.sb_model_id}), 201

@bp.get("/mappings")
@require_auth
@require_permissions("mappings:read")
def list_mappings():
    """List mappings."""
    items = Mapping.query.order_by(Mapping.created_at.desc()).all()
    return jsonify([{
        "id": m.id, "nb_model_id": m.nb_model_id, "sb_model_id": m.sb_model_id, "created_at": m.created_at.isoformat()
    } for m in items]), 200
