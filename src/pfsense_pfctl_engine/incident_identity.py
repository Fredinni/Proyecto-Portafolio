"""Label observed origin and victim addresses without inferring a NAT mapping."""

import ipaddress

PRIVATE_NETWORKS = tuple(ipaddress.ip_network(value) for value in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "fc00::/7"))


def address_scope(value):
    try:
        address = ipaddress.ip_address(value)
    except (ValueError, TypeError):
        return "unknown"
    if any(address.version == network.version and address in network for network in PRIVATE_NETWORKS):
        return "private"
    return "public" if address.is_global else "non_public"


def describe_network_identity(incident):
    """Derived fields: public means globally routable, never a tunnel's public peer."""
    origin = incident.get("attacker_ip")
    victim = incident.get("target_ip")
    unresolved = incident.get("source_identity") == "UNRESOLVED_PROXY"
    scope = address_scope(origin)
    public = origin if scope == "public" and not unresolved else None
    observed = incident.get("observed_source_ip") or origin
    return {
        "attacker_public_ip": public,
        "attacker_private_ip": origin if scope == "private" and not unresolved else None,
        "attacker_ip_scope": scope,
        "victim_ip": victim,
        "victim_private_ip": victim if address_scope(victim) == "private" else None,
        "observed_source_ip": observed,
        "origin_resolution": ("unresolved_proxy" if unresolved else
                              "trusted_proxy_xff" if observed != origin else "network_source"),
        "attacker_public_ip_status": ("observed" if public else
                                      "unresolved_proxy" if unresolved else
                                      "unavailable_internal_origin" if scope == "private" else
                                      "unavailable_non_public_origin"),
    }
