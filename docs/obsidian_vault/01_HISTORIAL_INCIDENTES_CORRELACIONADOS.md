---
aliases:
  - Historial de Incidentes Correlacionados
  - Bitácora SOAR KRONOS
tags:
  - incident-response
  - threat-intelligence
  - soar
  - pfsense
  - duoc-apt122
created: 2026-10-26
updated: 2026-10-26
author: Bruno Urrea Ortiz
rol: CISO & SecOps Lead
---

# 📋 Bitácora e Historial de Incidentes Correlacionados KRONOS

Base de conocimiento activa para correlación de vectores de ataque, detección de amenazas reincidentes y memoria histórica del agente de voz.

* **Reglas de Personalidad:** [[00_PERSONALIDAD_IA_KRONOS]]
* **Topología y Firewall:** [[02_TOPOLOGIA_Y_REGLAS_PFSENSE]]

---

## 1. Tabla de Correlación de Amenazas y Reincidencia

| # | Timestamp (UTC) | IP Atacante | Vector de Ataque | Tautología AST | Acción pfSense | Reincidencia | Estado CISO |
| :-: | :--- | :--- | :--- | :--- | :--- | :-: | :-: |
| 1 | 2026-10-26 00:54:12 | `185.220.101.5` | Inyección SQL Crítica | `'1'='1` | DROP en snort2c & State Kill | **x1** | Notificado |

---
| 2 | 2026-10-26 01:23:42 | `185.220.101.5` | Inyección SQL Crítica | `'1'='1` | DROP en snort2c & State Kill | ⚠️ **x2 (REINCIDENTE)** | En curso |
| 4 | 2026-10-26 01:26:18 | `185.220.101.5` | SQL_INJECTION (AST_TAUTOLOGY) | `1=1` | DROP & BLOCK en Firewall pfSense (Kernel pfctl State Kill) | ⚠️ **x4 (REINCIDENTE)** | En curso |
| 5 | 2026-10-26 01:33:14 | `185.220.101.5` | SQL_INJECTION (AST_TAUTOLOGY) | `1=1` | DROP & BLOCK en Firewall pfSense (Kernel pfctl State Kill) | ⚠️ **x5 (REINCIDENTE)** | En curso |

## 2. Detalle de Incidentes Registrados

### Caso #001: Inyección SQL hacia DVWA en DMZ
* **Fecha / Hora:** 2026-10-26 00:54:12 UTC
* **IP Origen:** `185.220.101.5` (Nodo Hostil Externo)
* **Objetivo:** `http://192.168.20.50/vulnerabilities/sqli/?id=1%27%20OR%20%271%27%3D%271%20--&Submit=Submit`
* **Análisis Sintáctico AST:** Confirmado `True` (Tautología booleana extraída: `'1'='1`).
* **Acción en Kernel:** Inserción en tabla `<snort2c>`, purga de socket con `pfctl -k 185.220.101.5`.
* **Despacho Telefónico:** Canal SIP `PJSIP/1001` (Bruno Urrea). Agente de voz Gemini Live reportó mitigación inmediata.

### Caso #002 - Reincidencia ⚠️ **x2 (REINCIDENTE)**: Inyección SQL Crítica
* **Timestamp:** 2026-10-26 01:23:42 UTC
* **IP Atacante:** `185.220.101.5`
* **Objetivo:** DVWA en DMZ
* **Tautologías AST:** `'1'='1`
* **Acción de Mitigación:** DROP en snort2c & State Kill
* **Frecuencia:** Este origen ha intentado atacar 2 veces.
* **Correlación:** [[00_PERSONALIDAD_IA_KRONOS]], [[02_TOPOLOGIA_Y_REGLAS_PFSENSE]]

### Caso #004 - Reincidencia ⚠️ **x4 (REINCIDENTE)**: SQL_INJECTION (AST_TAUTOLOGY)
* **Timestamp:** 2026-10-26 01:26:18 UTC
* **IP Atacante:** `185.220.101.5`
* **Objetivo:** DVWA en DMZ
* **Tautologías AST:** `1=1`
* **Acción de Mitigación:** DROP & BLOCK en Firewall pfSense (Kernel pfctl State Kill)
* **Frecuencia:** Este origen ha intentado atacar 4 veces.
* **Correlación:** [[00_PERSONALIDAD_IA_KRONOS]], [[02_TOPOLOGIA_Y_REGLAS_PFSENSE]]

### Caso #005 - Reincidencia ⚠️ **x5 (REINCIDENTE)**: SQL_INJECTION (AST_TAUTOLOGY)
* **Timestamp:** 2026-10-26 01:33:14 UTC
* **IP Atacante:** `185.220.101.5`
* **Objetivo:** DVWA en DMZ
* **Tautologías AST:** `1=1`
* **Acción de Mitigación:** DROP & BLOCK en Firewall pfSense (Kernel pfctl State Kill)
* **Frecuencia:** Este origen ha intentado atacar 5 veces.
* **Correlación:** [[00_PERSONALIDAD_IA_KRONOS]], [[02_TOPOLOGIA_Y_REGLAS_PFSENSE]]
