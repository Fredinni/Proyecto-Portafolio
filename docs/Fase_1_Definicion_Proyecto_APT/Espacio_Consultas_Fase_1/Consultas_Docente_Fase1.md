# Espacio de Consultas - Fase 1
### Registro de Consultas y Retroalimentación con el Docente Guía

---

### Consulta 1: Alcance del Laboratorio en DMZ
* **Pregunta planteada:**  
  *¿Es adecuado utilizar DVWA (Damn Vulnerable Web Application) como backend de pruebas publicado a través de HAProxy para validar las alertas de SQL Injection, o se recomienda desplegar una aplicación web comercial con API REST para la defensa final?*
* **Respuesta / Criterio Docente:**  
  *DVWA es un estándar reconocido para la validación de firmas en IPS/WAF. Se recomienda documentar los distintos niveles de seguridad (Low, Medium, High) y contrastar cómo Suricata y el motor pfctl bloquean los payloads en cada escenario.*

---

### Consulta 2: Integración de Telefonía y Latencia de IA
* **Pregunta planteada:**  
  *¿Existe alguna restricción respecto al uso de APIs de Inteligencia Artificial en tiempo real (Gemini Live API) para la automatización de llamadas de voz mediante Asterisk PBX?*
* **Respuesta / Criterio Docente:**  
  *Es una innovación destacada para el proyecto de título. Se debe asegurar que el tiempo total de respuesta desde el drop del paquete hasta la llamada telefónica se mantenga dentro de métricas aceptables de un SOC moderno (inferior a 5 segundos).*
