from flask import Blueprint, request, jsonify
from .auth import require_auth, require_permissions, audit
from .errors import error_response
from .models import Mapping, Model
from .utils import apply_mapping
from .southbound.netconf_client import send_netconf_rpc
from .southbound.snmp_cli_client import send_snmp_or_cli

bp = Blueprint("provision", __name__)

@bp.post("/provision")
@require_auth
@require_permissions("provision:execute")
def provision():
    """Trigger provisioning:
    Payload options:
    - { "mapping_id": int, "nb_model_id": int }
    or
    - { "mapping_id": int, "nb_inline": {...} }
    """
    data = request.get_json(silent=True) or {}
    mapping_id = data.get("mapping_id")
    if not mapping_id:
        return error_response("invalid_input", "mapping_id required", status=400)
    mapping: Mapping | None = Mapping.query.get(mapping_id)
    if not mapping:
        return error_response("not_found", "Mapping not found", status=404)

    nb_payload = data.get("nb_inline")
    if nb_payload is None:
        nb_id = data.get("nb_model_id")
        if not nb_id:
            return error_response("invalid_input", "nb_model_id or nb_inline required", status=400)
        nb_model = Model.query.get(nb_id)
        if not nb_model or nb_model.type != "NB":
            return error_response("invalid_input", "Invalid nb_model_id", status=400)
        nb_payload = nb_model.data

    sb_model = Model.query.get(mapping.sb_model_id)
    if not sb_model or sb_model.type != "SB":
        return error_response("invalid_input", "Invalid sb model on mapping", status=400)

    sb_payload = apply_mapping(nb_payload, mapping.mapping_data)
    protocol = mapping.mapping_data.get("protocol", "NETCONF").upper()

    # Stub southbound call
    if protocol == "NETCONF":
        ok, result = send_netconf_rpc(sb_payload)
    elif protocol in ("SNMP", "CLI"):
        ok, result = send_snmp_or_cli(protocol, sb_payload)
    else:
        return error_response("invalid_input", f"Unsupported protocol {protocol}", status=400)

    audit("provision", None, {"mapping_id": mapping.id, "protocol": protocol, "success": ok, "result": result})
    if ok:
        return jsonify({"success": True, "protocol": protocol, "result": result}), 200
    return error_response("provision_failed", "Provisioning failed", {"result": result}, status=500)
