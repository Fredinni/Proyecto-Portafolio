"""Read the installed MaxMind MMDB files; never infer countries from prefixes."""

import ipaddress
import os
from pathlib import Path


class GeoIPLookup:
    def __init__(self, config=None, opener=None):
        config = config or {}
        self.city_db = os.getenv("KRONOS_GEOIP_DB", config.get("db_path", ""))
        self.asn_db = os.getenv("KRONOS_GEOIP_ASN_DB", config.get("asn_db_path", ""))
        self.opener = opener

    def _read(self, database, ip):
        if self.opener:
            with self.opener(database) as reader:
                return reader.get(ip) or {}
        if not database or not Path(database).is_file():
            return {}
        import maxminddb
        with maxminddb.open_database(database) as reader:
            return reader.get(ip) or {}

    def lookup(self, ip):
        result = {"status": "unavailable", "country": None, "country_code": None,
                  "city": None, "source": None,
                  "limitation": "Ubicación aproximada de la IP, no identidad ni ubicación comprobada de la persona."}
        try:
            address = ipaddress.ip_address(ip)
        except (ValueError, TypeError):
            return {**result, "status": "invalid_ip"}
        if not address.is_global:
            return {**result, "status": "non_public", "country": "IP privada o reservada; sin geolocalización pública"}
        try:
            data = self._read(self.city_db, str(address))
            country = data.get("country", {})
            country_names = country.get("names", {})
            if country.get("iso_code"):
                result.update({"status": "found", "country": country_names.get("es") or country_names.get("en"),
                               "country_code": country["iso_code"],
                               "city": data.get("city", {}).get("names", {}).get("es") or
                                       data.get("city", {}).get("names", {}).get("en"),
                               "accuracy_radius_km": data.get("location", {}).get("accuracy_radius"),
                               "source": Path(self.city_db).name})
            if self.asn_db:
                asn = self._read(self.asn_db, str(address))
                result.update({"asn": asn.get("autonomous_system_number"),
                               "asn_organization": asn.get("autonomous_system_organization")})
        except Exception:
            # GeoIP is optional enrichment. Missing modules, permissions or a
            # corrupt MMDB must not stop incident containment and notification.
            result["status"] = "unavailable"
        return result
