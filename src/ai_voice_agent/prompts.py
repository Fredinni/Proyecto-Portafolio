"""
KRONOS SENTINEL - Optimized Voice Prompts with Dynamic Variables, Chilean Telephony Flow & Function Calling
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
"""

import json

# Definición de Function Calling Tools para SOAR autónomo en llamadas Gemini Live
SOAR_FUNCTION_TOOLS = [
    {
        "name": "block_ip_permanently",
        "description": "Inserta permanentemente la dirección IP en la tabla snort2c de FreeBSD pfctl y purga conexiones activas.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "ip": {
                    "type": "STRING",
                    "description": "Dirección IPv4 del atacante a bloquear perimetralmente."
                },
                "reason": {
                    "type": "STRING",
                    "description": "Justificación táctica de la mitigación."
                }
            },
            "required": ["ip"]
        }
    },
    {
        "name": "unblock_ip",
        "description": "Retira la dirección IP de la tabla snort2c si el CISO determina que es falso positivo o tráfico de testing.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "ip": {
                    "type": "STRING",
                    "description": "Dirección IP a desbloquear."
                },
                "reason": {
                    "type": "STRING",
                    "description": "Motivo del desbloqueo autorizado por el CISO."
                }
            },
            "required": ["ip", "reason"]
        }
    },
    {
        "name": "get_firewall_states",
        "description": "Consulta en tiempo real los estados de conexión activos en el kernel pfSense para una IP específica.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "ip": {
                    "type": "STRING",
                    "description": "Dirección IP a inspeccionar."
                }
            },
            "required": ["ip"]
        }
    },
    {
        "name": "escalate_to_soc_tier2",
        "description": "Escala el incidente a nivel crítico y despacha notificación al equipo de respuesta a incidentes.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "incident_id": {
                    "type": "STRING",
                    "description": "Identificador único del incidente."
                },
                "priority": {
                    "type": "STRING",
                    "enum": ["MEDIA", "ALTA", "CRITICA"]
                },
                "notes": {
                    "type": "STRING",
                    "description": "Instrucciones dictadas por el CISO durante la llamada."
                }
            },
            "required": ["incident_id", "priority"]
        }
    }
]

def build_system_prompt_informal(incident_data: dict) -> str:
    """Genera el System Instruction dinámico con variables reales y flujo de telefonía chilena"""
    attack_type = incident_data.get('attack_type', 'Intrusión L7')
    attacker_ip = incident_data.get('attacker_ip', 'IP desconocida')
    target = incident_data.get('target_service', 'DVWA en DMZ')
    geo = incident_data.get('geo_country', 'Nodo no identificado')
    confidence = incident_data.get('confidence_score', 0.90) * 100
    is_blocked = incident_data.get('pfctl_blocked', True)
    pf_action = "le chantó DROP en la tabla snort2c y mató todos los estados" if is_blocked else "está en observación pendiente de tu confirmación"

    return (
        "Eres la operadora de IA del sistema KRONOS SENTINEL. "
        "Estás en una llamada telefónica en vivo con Bruno Urrea (CISO). "
        "HABLA DE TÚ A TÚ, SÚPER INFORMAL, MUY CASUAL, COMO UNA COLEGA CAPA Y RELAJADA. "
        "Cero formalismos corporativos. "
        "FLUJO DE TELEFONÍA CHILENA: Empieza siempre saludando como se hace en Chile: '¿Aló, Bruno? Oye...'. "
        f"Datos dinámicos del ataque: "
        f"- Tipo de Incidente: {attack_type}. "
        f"- Atacante: IP {attacker_ip} ({geo}). "
        f"- Objetivo: {target}. "
        f"- Nivel de certeza: {confidence:.0f}%. "
        f"- Acción ejecutada: El pfSense ya {pf_action}. "
        "Explícale la situación en máximo 28 palabras y pregúntale qué hacemos: si revisamos el tráfico o si lo dejamos bloqueado nomás. "
        "Devuelve SOLO el diálogo que vas a pronunciar por voz."
    )

def build_farewell_prompt(incident_data: dict) -> str:
    """Genera el prompt de despedida dinámico"""
    attacker_ip = incident_data.get('attacker_ip', 'el atacante')
    return (
        "Eres la operadora de IA de KRONOS cerrando la llamada con Bruno Urrea. "
        "HABLA DE TÚ A TÚ, SÚPER INFORMAL, MUY CASUAL. "
        f"Dile que la IP {attacker_ip} ya quedó sellada en el pfSense y que ante cualquier cosa le timbras al tiro. "
        "Despídete con buena onda. Máximo 16 palabras. Devuelve SOLO el diálogo a pronunciar."
    )
