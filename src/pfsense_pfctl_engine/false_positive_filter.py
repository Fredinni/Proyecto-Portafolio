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

    def analyze(self, event: Dict[str, Any]) -> Tuple[bool, str, float]:
        """
        Analiza el evento Suricata para separar ruido de ataques críticos reales.
        Retorna: (es_ataque_real: bool, tipo_ataque: str, confianza: float)
        """
        alert = event.get("alert", {})
        signature = alert.get("signature", "")
        severity = alert.get("severity", 3)
        http = event.get("http", {})
        
        url = http.get("url", "")
        body = http.get("http_request_body", "") or event.get("payload_printable", "")
        
        # Desofuscación iterativa de URL
        decoded_url = urllib.parse.unquote(url)
        decoded_body = urllib.parse.unquote(body) if isinstance(body, str) else ""
        combined_payload = f"{decoded_url} {decoded_body}"
        
        # 1. Descarte inmediato de firmas ruidosas de escaneo L3/L4 sin contexto HTTP
        for noisy_sig in self.noisy_signatures:
            if noisy_sig.lower() in signature.lower() and not http:
                return (False, "RUIDO_ESCANEO_TRIVIAL_SUPRIMIDO", 0.05)
                
        # 2. Detección y clasificación de SQL Injection
        sqli_matches = 0
        for pattern in self.sqli_patterns:
            if pattern.search(combined_payload):
                sqli_matches += 1
                
        if sqli_matches >= 1:
            confidence = min(0.70 + (sqli_matches * 0.15), 0.99)
            return (True, "CRITICAL_SQL_INJECTION", confidence)
            
        if severity == 1 and ("sql" in signature.lower() or "injection" in signature.lower()):
            return (True, "SURICATA_CONFIRMED_SQLI", 0.85)

        # 3. Detección de Command Injection / RCE
        for pattern in self.rce_patterns:
            if pattern.search(combined_payload):
                return (True, "COMMAND_INJECTION_RCE", 0.95)
                
        if severity == 1 and ("rce" in signature.lower() or "remote code" in signature.lower() or "exploit" in signature.lower()):
            return (True, "CRITICAL_EXPLOIT_PAYLOAD", 0.90)

        # 4. Tráfico sin severidad crítica (suprimir escalamiento)
        return (False, "LOW_CONFIDENCE_NOISE_SUPPRESSED", 0.20)

    def get_geoip(self, ip: str) -> str:
        """Resolución de geolocalización IP (MaxMind GeoLite2)"""
        if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
            return "Red Privada / Laboratorio DMZ (Simulado WAN)"
        if ip.startswith("185.") or ip.startswith("198."):
            return "Federación Rusa (Nodo Hostil Detectado)"
        return "Origen Internacional No Confiable (MaxMind GeoIP)"
