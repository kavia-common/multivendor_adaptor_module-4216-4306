from typing import Any, Dict

# PUBLIC_INTERFACE
def validate_required(data: Dict[str, Any], required: list[str]) -> list[str]:
    """Return list of missing required keys from a dict."""
    return [k for k in required if k not in data or data[k] in (None, "")]

# PUBLIC_INTERFACE
def apply_mapping(nb_json: Dict[str, Any], mapping_data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply a simple mapping to transform NB JSON to SB payload.
    mapping_data example:
    {
      "protocol": "NETCONF" | "SNMP" | "CLI",
      "mappings": [
        {"from": "customer.name", "to": "device.config.customerName"},
        {"from": "service.vlan", "to": "device.config.vlanId"}
      ]
    }
    """
    def get_nested(d: Dict[str, Any], path: str):
        cur = d
        for p in path.split("."):
            if not isinstance(cur, dict) or p not in cur:
                return None
            cur = cur[p]
        return cur

    def set_nested(d: Dict[str, Any], path: str, value: Any):
        parts = path.split(".")
        cur = d
        for p in parts[:-1]:
            if p not in cur or not isinstance(cur[p], dict):
                cur[p] = {}
            cur = cur[p]
        cur[parts[-1]] = value

    sb = {}
    for m in mapping_data.get("mappings", []):
        src = m.get("from")
        dst = m.get("to")
        if not src or not dst:
            continue
        val = get_nested(nb_json, src)
        if val is not None:
            set_nested(sb, dst, val)
    return sb
