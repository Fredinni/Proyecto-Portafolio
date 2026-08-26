#!/usr/bin/env python3
"""
KRONOS SENTINEL - Gemini Live API (Flash 3.1 / 2.0) Bidirectional Voice Client
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from prompts import SYSTEM_INSTRUCTION_CISO_CALL, generate_incident_context_prompt

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [GEMINI-LIVE] %(message)s')

class GeminiLiveVoiceClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "MOCK_KEY_FOR_LOCAL_SIMULATION")
        self.model = "gemini-2.0-flash-exp" # o gemini-3.1-flash-live
        self.ws_url = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={self.api_key}"
        
    async def start_voice_session(self, incident_data: Dict[str, Any], audio_input_stream=None, audio_output_stream=None):
        """Inicia sesión bidireccional de voz con Gemini Live API conectada al bridge de Asterisk"""
        context_prompt = generate_incident_context_prompt(incident_data)
        logging.info("Estableciendo túnel WebSocket con Gemini Live API para streaming de audio PCM 24kHz...")
        logging.info(f"Contexto cargado: Incidente {incident_data.get('attack_type')} desde {incident_data.get('attacker_ip')}")

        setup_message = {
            "setup": {
                "model": f"models/{self.model}",
                "generationConfig": {
                    "responseModalities": ["AUDIO", "TEXT"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {
                                "voiceName": "Fenrir" # Voz táctica, profunda y ejecutiva
                            }
                        }
                    }
                },
                "systemInstruction": {
                    "parts": [{"text": SYSTEM_INSTRUCTION_CISO_CALL + "\n" + context_prompt}]
                }
            }
        }
        
        logging.info(f"Sesión Gemini Live configurada con voz táctica 'Fenrir'. Lista para interacción por audio.")
        # Simulación de handshake de llamada
        return True

if __name__ == "__main__":
    client = GeminiLiveVoiceClient()
    dummy_incident = {
        "attack_type": "SQL Injection Crítica (UNION SELECT)",
        "attacker_ip": "185.220.101.5",
        "geo_country": "Federación Rusa (Tor Exit Node)",
        "http_endpoint": "/vulnerabilities/sqli/?id=1%27%20UNION%20SELECT%20null,user,password%20FROM%20users--",
        "confidence_score": 0.98
    }
    asyncio.run(client.start_voice_session(dummy_incident))
