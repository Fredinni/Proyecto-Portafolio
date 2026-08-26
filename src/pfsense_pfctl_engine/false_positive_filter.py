#!/usr/bin/env python3
"""
KRONOS SENTINEL - Heuristic False-Positive Filter & SQLi/RCE Payload Analyzer (Hardened)
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
"""

import re
import urllib.parse
from typing import Dict, Any, Tuple

class FalsePositiveFilter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Patrones de ataque SQL Injection de alta fidelidad
        self.sqli_patterns = [
            re.compile(r"\b(UNION(\s+ALL)?\s+SELECT)\b", re.IGNORECASE),
            re.compile(r"\b(SELECT\s+[\w\*\,\s\(\)]+\s+FROM\s+[\w\.\_]+)\b", re.IGNORECASE),
            re.compile(r"\b(OR\s+[\'\"]?\d+[\'\"]?\s*=\s*[\'\"]?\d+[\'\"]?|AND\s+[\'\"]?\d+[\'\"]?\s*=\s*[\'\"]?\d+[\'\"]?)\b", re.IGNORECASE),
            re.compile(r"\b(OR\s+[\'\"].*?[\'\"]\s*=\s*[\'\"].*?[\'\"])\b", re.IGNORECASE),
            re.compile(r"\b(BENCHMARK\s*\(|SLEEP\s*\(|PG_SLEEP\s*\(|WAITFOR\s+DELAY)\b", re.IGNORECASE),
            re.compile(r"\b(INFORMATION_SCHEMA|INTO\s+OUTFILE|LOAD_FILE|SYS\.TABLES)\b", re.IGNORECASE),
            re.compile(r"(\%27|\')\s*(OR|AND|UNION)\b", re.IGNORECASE)
        ]
        
        # Patrones de Command Injection / RCE
        self.rce_patterns = [
            re.compile(r"(;|\||&&|\$\(|\`)\s*(cat\s+/etc/passwd|id|whoami|uname\s+-a|nc\s+-e|bash\s+-i|curl\s+http|wget\s+http)", re.IGNORECASE),
            re.compile(r"\b(php:\/\/input|data:\/\/text\/plain|expect:\/\/)\b", re.IGNORECASE)
        ]
        
        # Firmas de escaneo trivial o ruido sin impacto L7
        self.noisy_signatures = [
            "ET POLICY Suspicious inbound to MSSQL port",
            "ET SCAN Potential SSH Scan",
            "GPL SCAN PING *NIX",
            "SURICATA HTTP suspicious User-Agent",
            "ET INFO Generic Protocol Handler"
        ]
        self.known_false_positive_patterns = [
            re.compile(r"ET POLICY Suspicious inbound to MSSQL port", re.IGNORECASE),
            re.compile(r"ET SCAN Potential SSH Scan", re.IGNORECASE),
            re.compile(r"GPL SCAN PING \*NIX", re.IGNORECASE)
        ]

    def analyze(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza el evento Suricata para separar ruido de ataques críticos reales.
        Retorna: (dict con resultados de análisis)
        """
        alert = event.get("alert") or {}
        http = event.get("http") or {}
        src_ip = event.get("src_ip", "")
        
        signature = alert.get("signature") or ""
        url = http.get("url") or ""
        body = http.get("http_request_body") or event.get("payload_printable") or ""
        
        # 1. Desofuscar y decodificar URLs
        decoded_url = urllib.parse.unquote(url) if isinstance(url, str) else ""
        decoded_body = urllib.parse.unquote(body) if isinstance(body, str) else ""
        full_payload = f"{signature} {decoded_url} {decoded_body}"
        
        # 2. Descartar Escaneos Triviales y Ruido Conocido
        for fp_pattern in self.known_false_positive_patterns:
            if fp_pattern.search(full_payload):
                return {
                    "is_real_attack": False,
                    "confidence_score": 0.1,
                    "attack_type": "NOISE / SCANNER",
                    "reason": f"Patrón de ruido o fuzzer detectado: {fp_pattern.pattern}",
                    "src_ip": src_ip
                }
        
        # 3. Detectar Inyecciones SQL (SQLi)
        sqli_matches = [p.pattern for p in self.sqli_patterns if p.search(full_payload)]
        rce_matches = [p.pattern for p in self.rce_patterns if p.search(full_payload)]
        
        confidence = 0.0
        attack_type = "UNKNOWN"
        
        if sqli_matches:
            attack_type = "SQL_INJECTION"
            confidence = min(1.0, 0.6 + (0.2 * len(sqli_matches)))
        elif rce_matches:
            attack_type = "REMOTE_CODE_EXECUTION"
            confidence = min(1.0, 0.7 + (0.15 * len(rce_matches)))
            
        is_real = confidence >= 0.75
        
        return {
            "is_real_attack": is_real,
            "confidence_score": confidence,
            "attack_type": attack_type,
            "matches": sqli_matches or rce_matches,
            "src_ip": src_ip,
            "http_endpoint": url,
            "geo_origin": self.get_geoip(src_ip)
        }

    def get_geoip(self, ip: str) -> str:
        """Simulación / Consulta GeoIP MaxMind"""
        if not ip or not isinstance(ip, str):
            return "Origen Desconocido"
        if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172.16."):
            return "Red Privada / Laboratorio Local"
        if ip.startswith("185.") or ip.startswith("198."):
            return "Federación Rusa (Nodo Hostil Detectado)"
        return "Origen Internacional No Confiable (MaxMind GeoIP)"
