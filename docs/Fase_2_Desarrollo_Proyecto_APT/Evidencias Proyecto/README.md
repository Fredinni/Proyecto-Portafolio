# Evidencias técnicas del proyecto

Este índice reúne las evidencias que antes estaban distribuidas entre `docs/`, `assets/` e `infra/`. Se conservan los archivos originales y se referencian desde Fase 2 para evitar copias divergentes. Las capturas históricas acreditan su fecha de captura; no sustituyen una comprobación actual.

| Evidencia | Ubicación | Qué permite revisar |
|---|---|---|
| Respaldo real de pfSense sanitizado | [Configuraciones](Configuraciones/) | Exportación del equipo, origen, fecha y campos retirados. Es evidencia documental y no debe restaurarse. |
| Infraestructura y segmentación | [Despliegue Proxmox](../../PROXMOX_ONPREM_DEPLOYMENT.md) · [Automatización de infraestructura](../../../infra/proxmox/) | VMs, VLAN, reglas y procedimientos reproducibles. Las credenciales operativas están fuera de Git. |
| Configuración base de pfSense | [Código y verificadores](../../../src/pfsense_setup/) | Ajustes de interfaz y comprobaciones del sistema. |
| IPS, correlación y bloqueo | [Motor de correlación](../../../src/pfsense_pfctl_engine/) · [Auditoría integral histórica](../../AUDITORIA_INTEGRAL_A1_A7_KRONOS.md) | Lectura de eventos, filtro, identidad del origen y acciones sobre PF. |
| Voz conversacional y autorización SOAR | [Operación Gemini Live](../../GEMINI_LIVE_OPERACION.md) · [Código del agente](../../../src/ai_voice_agent/) | Sesión de audio bidireccional, herramientas y autorización de desbloqueo. |
| Servicios y plantillas de despliegue | [Servicios de voz](../../../infra/proxmox/services/) · [Telefonía Asterisk](../../../src/asterisk_pbx/) | Configuración parametrizada y ejemplos sin secretos. |
| Validación operativa del 16 de noviembre | [Resultados y límites](../../VALIDACION_OPERATIVA_2026-11-16.md) | Despliegue observado y recuperación del entorno de pruebas. |
| SQLi y notificación del 16 de noviembre | [Validación QA](../../VALIDACION_QA_SQLI_2026-11-16.md) | Pruebas autorizadas con DVWA Low y flujo de llamada; el IPS permanece activo. |
| IP pública, víctima privada y audio | [Identidad y estabilidad](../../VALIDACION_ESTABILIDAD_VOZ_2026-11-16.md) | Lectura de la evidencia en pfSense, desbloqueo verificado y tiempos medidos de llamadas. |
| Capturas de integración A7 | [Capturas originales](../../evidencias_a7/) | Evidencias visuales históricas del laboratorio. |
| Avance A1 del 27 de septiembre | [Archivos y capturas](Avance_A1_2026-09-27/) | Evidencia de implementación temprana, separada del estado actual. |
| Topología e ilustraciones | [Recursos gráficos](../../../assets/) | Apoyo visual de la arquitectura; las ilustraciones por sí solas no prueban funcionamiento. |
| Memoria de amenazas | [Módulo de memoria](../../../src/pfsense_pfctl_engine/obsidian_memory_manager.py) · [Documentación histórica](../../obsidian_vault/) | Componente disponible; su presencia no acredita que esté conectado al flujo Live desplegado. |
| Pruebas reproducibles | [Pruebas del proyecto](../../../tests/) · [Workflow CI](../../../.github/workflows/tests.yml) | Pruebas con dobles y validaciones locales; no equivalen a una prueba telefónica del usuario. |

## Lectura correcta de la demostración

Suricata conserva la prevención inmediata. La IA agrega notificación, explicación y acciones autorizadas sobre el bloqueo. Un ataque descartado debe generar telemetría desde el sensor; no es necesario dejarlo llegar a DVWA para avisar. Desbloquear una IP no crea una excepción permanente: otro ataque puede bloquearla de nuevo.

La IP pública solo se anuncia cuando existe evidencia observable en pfSense. En recorridos internos por Tailscale puede no estar disponible; la IA debe decirlo. MaxMind/GeoLite2 se consulta en pfSense y no dentro del modelo.

## Alcance y resguardo

Los resultados de laboratorio tienen el alcance y fecha indicados en cada validación. No acreditan protección total, ausencia de falsos positivos, disponibilidad permanente ni costos operativos nulos. DVWA es un objetivo vulnerable de laboratorio; las pruebas se limitan al entorno autorizado. El acceso del equipo se documenta de forma parametrizada en [TEAM_LAB_ACCESS](../../TEAM_LAB_ACCESS.md).
