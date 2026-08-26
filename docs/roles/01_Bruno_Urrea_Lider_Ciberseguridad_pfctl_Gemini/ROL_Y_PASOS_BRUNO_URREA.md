# GUÍA DE ROL Y MANUAL OPERATIVO: LÍDER DE CIBERSEGURIDAD, MOTOR PFCTL E INTEGRACIÓN GEMINI LIVE
## Integrante: Bruno Urrea Ortiz
**Carrera:** Ingeniería en Conectividad y Redes — Duoc UC Sede San Joaquín  
**Asignatura:** Portafolio de Título (APT122) — Proyecto KRONOS SENTINEL  
**Rol Oficial:** *Líder de Arquitectura de Ciberseguridad, Motor de Correlación pfctl e Integración Gemini Live API*

---

## 1. MISIÓN Y RESPONSABILIDADES PRINCIPALES

Como Líder de Arquitectura de KRONOS SENTINEL, eres el responsable del **núcleo de inteligencia, correlación y orquestación SOAR**:

1. **Desarrollo y Mantenimiento del Motor `pfctl` (Python 3.12):**
   * Supervisar la ingesta en tiempo real del archivo `/var/log/suricata/eve.json`.
   * Mantener el algoritmo de supresión de falsos positivos (`false_positive_filter.py`), garantizando el descarte de más del 50% de alertas ruidosas.
   * Ejecutar la validación heurística mediante análisis AST (*Abstract Syntax Tree*) de payloads SQLi y patrones RCE.
   * Administrar las llamadas atómicas al kernel de FreeBSD (`pfctl_wrapper.py`) para verificar la persistencia en la tabla en memoria RAM `<snort2c>`.
2. **Integración con Google Gemini Live API Flash 3.1:**
   * Desarrollar y gestionar el cliente WebSocket seguro HTTPS (`gemini_live_client.py`).
   * Diseñar los System Prompts tácticos de ciberseguridad (`prompts.py`) para que la IA actúe como un analista SOC de guardia, informando IP, país GeoIP, payload del vector y confirmación del bloqueo en firewall.
   * Gestionar la cuota gratuita (*Google AI Studio Free Tier*) para asegurar costo $0 CLP en la defensa presencial.
3. **Orquestación Global y Despacho de Webhooks:**
   * Gestionar el demonio despachador (`dispatcher.py`), puenteando las alertas confirmadas hacia el auto-dialer de Asterisk PBX.

---

## 2. CHECKLIST PASO A PASO PARA EL DESPLIEGUE TÉCNICO

### Fase A: Puesta en Marcha del Motor de Correlación
```bash
# 1. Acceder al directorio del motor:
cd src/pfsense_pfctl_engine

# 2. Validar sintaxis y configuración YAML:
python -c "import yaml; print(yaml.safe_load(open('config.yaml')))"

# 3. Iniciar el demonio de correlación:
python log_correlator.py
```

### Fase B: Puesta en Marcha del Agente de Voz Gemini Live
```bash
# 1. Acceder al directorio del agente de voz:
cd src/ai_voice_agent

# 2. Exportar la API Key gratuita de Google AI Studio:
export GEMINI_API_KEY="AIzaSy..."

# 3. Iniciar el servidor despachador:
python dispatcher.py
```

### Fase C: Prueba de Simulación de Inyección SQL y Validación Atómica
```bash
# Disparar prueba de inyección SQL simulada:
curl -s -X POST http://127.0.0.1:8000/incident \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "185.220.101.5",
    "dest_ip": "198.51.100.1",
    "attack_type": "SQL Injection",
    "payload": "admin'\'' OR '\''1'\''='\''1 --",
    "country": "Rusia (GeoIP)",
    "rule_id": "2008287",
    "status": "BLOCKED_IN_KERNEL"
  }'
```

---

## 3. GUÍA DE DEFENSA ANTE LA COMISIÓN EVALUADORA (PREGUNTAS CLAVE)

### P1: "¿Por qué crearon un motor de correlación en Python en lugar de dejar que pfSense bloquee todo directamente?"
* **Respuesta Senior:** *"Profesor, si dejamos que el firewall o Suricata bloqueen y alerten por cada firma, saturamos la centralita con falsos positivos y generamos fatiga de alertas extrema. El motor `pfctl` analiza la estructura sintáctica del payload (AST), evalúa si hay operadores relacionales reales y comprueba que la IP esté efectivamente en la tabla en memoria `<snort2c>` del kernel de FreeBSD antes de escalar la llamada al CISO."*

### P2: "¿Cómo opera la comunicación con Gemini Live API sin violar la restricción de costo $0?"
* **Respuesta Senior:** *"Utilizamos la capa gratuita Google AI Studio Free Tier para el modelo Gemini Live Flash 3.1. La conexión se establece por WebSocket seguro saliente (puerto TCP 443), lo que además evade restricciones de CGNAT y bloqueos de puertos entrantes en la sede Duoc UC."*
