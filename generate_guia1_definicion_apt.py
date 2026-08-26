#!/usr/bin/env python3
"""
Generador Maestro: Guía 1 - Definición Proyecto APT (Fase 1)
Asignatura: Portafolio de Título (APT122) - Duoc UC Sede San Joaquín
Genera las 3 versiones oficiales: Markdown (.md), Word (.docx) y PDF (.pdf).
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# =============================================================================
# 1. CONTENIDO COMPLETO EN MARKDOWN
# =============================================================================
MARKDOWN_CONTENT = """# Guía 1. Definición Proyecto APT
### Asignatura: Portafolio de Título (APT122) — Fase 1
**Institución:** Duoc UC — Sede San Joaquín  
**Escuela:** Escuela de Informática y Telecomunicaciones  
**Carrera:** Ingeniería en Conectividad y Redes  
**Estudiante:** Bruno Urrea Ortiz  

---

# A. PARTE I

## 1. Antecedentes Personales

| Campo | Información Solicitada |
| :--- | :--- |
| **Nombre estudiante** | Bruno Urrea Ortiz |
| **Rut** | 21.543.637-3 |
| **Carrera** | Ingeniería en Conectividad y Redes |
| **Sede** | San Joaquín |
| **Integrantes del Equipo (Grupal)** | • Bruno Urrea Ortiz (Líder de Ciberseguridad, Motor KRONOS y Gemini Live)<br>• Freddy Vásquez Cortés (Routing, Switching y Telefonía Asterisk PBX)<br>• Cristóbal Quezada (Servicios Web, HAProxy SSL y DMZ DVWA)<br>• Kevin Retamales (Hardening Perimetral, pfBlockerNG y QA) |

---

## 2. Descripción Proyecto APT

| Campo | Detalle |
| :--- | :--- |
| **Nombre del proyecto** | **KRONOS SENTINEL:** Autonomous AI-IPS & Real-Time Incident Voice Response SOAR Architecture |
| **Área(s) de desempeño** | • Seguridad de la Información, Ciberseguridad Defensiva y Hardening Perimetral.<br>• Infraestructura de Redes Corporativas, Routing y Switching L2/L3 (VLANs 802.1Q).<br>• Telecomunicaciones, Telefonía VoIP SIP/PJSIP y Streaming de Audio en Tiempo Real.<br>• Automatización, Programación en Python e Integración de Inteligencia Artificial (SOAR). |
| **Competencias** | • **Competencia 3:** Adaptar tecnologías de punta y tendencias emergentes de conectividad.<br>• **Competencia 4:** Controlar y operar redes corporativas de gran tamaño.<br>• **Competencia 5:** Unificar servicios de voz, datos y video.<br>• **Competencia 6:** Automatizar procesos y gestión de plataformas de red.<br>• **Competencia 7:** Gestionar la seguridad de la información frente a vulnerabilidades.<br>• **Competencia 8:** Crear planes de prevención y respuesta a riesgos informáticos. |

---

## 3. Fundamentación Proyecto APT

### 3.1 Relevancia del proyecto APT
* **¿Por qué se escogió este tema?** En la industria de la ciberseguridad corporativa moderna, los Centros de Operaciones de Seguridad (SOC) y los firewalls perimetrales enfrentan dos fallas estructurales críticas:
  1. *La crisis de hiper-alerta y falsos positivos:* Los motores de inspección profunda como Suricata o Snort generan más de un 50% de alertas ruidosas e inocuas (escaneos automáticos de puertos, crawlers web y firmas no explotables), saturando las colas de incidentes.
  2. *El colapso cognitivo del operador humano bajo presión:* Ante una intrusión real y de alto impacto (ej. inyecciones SQL masivas o exploits RCE), el analista SOC entra en visión de túnel y pánico, viéndose obligado a investigar y mitigar en la consola del firewall y, al mismo tiempo, redactar reportes o llamar al CISO (Chief Information Security Officer). Al intentar hacer ambas tareas a la vez, se cometen errores de digitación, se bloquea la comunicación verbal y la contención se retrasa críticamente.
* **¿Dónde se ubica la situación?** Se sitúa en infraestructuras corporativas empresariales, entidades financieras, instituciones de educación superior y organizaciones con servicios web expuestos a Internet en Chile y Latinoamérica.
* **¿A quiénes impacta?** Impacta directamente a los equipos de ingeniería de seguridad (SOC Nivel 1/2/3), a los CISOs y decisores estratégicos, y a la continuidad operativa de los servicios digitales corporativos.
* **¿Cuál es el aporte de valor?** KRONOS SENTINEL aporta una solución **SOAR (Security Orchestration, Automation and Response) de Costo Cero ($0 CLP)** que desacopla la contención técnica de la comunicación estratégica: ejecuta la mitigación atómica en el kernel de FreeBSD en microsegundos (<100 ms) y, de forma simultánea, realiza una llamada telefónica interactiva con Inteligencia Artificial conversacional (Google Gemini Live Flash 3.1) para entregar un debriefing táctico hablado en tiempo real (<1.5 s).

### 3.2 Descripción del Proyecto APT
El proyecto consiste en el diseño, implementación y validación de una arquitectura de defensa en profundidad compuesta por:
1. **Perímetro Fortificado:** Firewall **pfSense CE 2.9.0** con **Suricata 7.x en modo Inline IPS (Netmap)** para descarte de paquetes en hardware sin latencia, y **pfBlockerNG-devel** con inteligencia GeoIP MaxMind y listas de reputación global (FireHOL, Spamhaus).
2. **Capa Web DMZ:** Proxy inverso **HAProxy 2.8+** con SSL Offloading (puerto 443) y *Stick-Tables* dinámicas en RAM para mitigación de DoS/Fuzzing L7, protegiendo un laboratorio vulnerable controlado (**DVWA** en Docker, VLAN 20).
3. **Motor de Correlación KRONOS (Python 3.12):** Daemon asíncrono que ingesta `eve.json`, suprime más del 50% de falsos positivos mediante análisis sintáctico AST de payloads SQLi/RCE y utiliza **`pfctl`** (la herramienta de kernel de FreeBSD) para terminar estados activos (`pfctl -k`) y verificar la tabla dinámica `<snort2c>`.
4. **Respuesta Telefónica Autónoma SOAR:** Centralita **Asterisk 20 LTS** en Docker que ejecuta un auto-dialer AMI hacia el softphone del CISO, conectando el flujo de audio RTP con **Google Gemini Live Flash 3.1** mediante WebSocket para interactuar por voz en lenguaje natural.

### 3.3 Pertinencia del proyecto con el perfil de egreso
El proyecto integra de forma armónica las 4 áreas troncales de la carrera de Ingeniería en Conectividad y Redes:
* **Networking & Switching:** Segmentación L2/L3 en 4 VLANs (Corp 10, DMZ 20, VoIP 30, Mgmt 99) sobre troncal 802.1Q.
* **Seguridad Perimetral:** Hardening de kernel FreeBSD, configuración de reglas Zero Trust, listas de amenazas y prevención IPS Inline.
* **Telefonía VoIP:** Despliegue de centralita Asterisk PBX, protocolo SIP/PJSIP, Dialplans y códecs de audio en tiempo real.
* **Automatización y Programación:** Desarrollo de software en Python, manejo de sockets IPC, parsing estructurado JSON y consumo de APIs de IA generativa multimodal.

### 3.4 Relación con los intereses profesionales
KRONOS SENTINEL se alinea directamente con mi meta profesional de desempeñarme como **Ingeniero de Ciberseguridad / Arquitecto de Infraestructura y SecOps**, especializándome en arquitecturas Zero Trust, mitigación perimetral y automatización de respuesta ante incidentes. Asimismo, consolida la experiencia técnica adquirida liderando el equipo de competiciones CTF **DevSec** y en despliegues tecnológicos de alta concurrencia.

### 3.5 Factibilidad de desarrollo del Proyecto APT
* **(1) Duración del semestre:** 18 semanas académicas planificadas cronológicamente.
* **(2) Horas asignadas:** 72 horas presenciales de taller de titulación más 144 horas de trabajo autónomo en laboratorio.
* **(3) Materiales requeridos:** Arquitectura 100% de Costo Cero ($0 CLP), basada en software libre y código abierto (FreeBSD, pfSense CE, Suricata, Asterisk, Docker, Python) y capas gratuitas comunitarias (Google AI Studio Free Tier para Gemini Live, MaxMind Free Tier).
* **(4) Factores externos que facilitan el desarrollo:** Disponibilidad de laboratorios en Duoc UC San Joaquín, soporte multiplataforma de virtualización (Proxmox VE / VMware) y documentación oficial de Netgate.
* **(5) Factores externos que dificultan y solución:**
  * *Dificultad:* Presencia de CGNAT o bloqueo de puertos entrantes en redes residenciales o institucionales.
  * *Solución Técnica:* Implementación de malla VPN Zero Trust con **Tailscale Subnet Router**, permitiendo que el softphone del CISO acceda a la subred de telefonía (`192.168.30.0/24`) mediante túnel WireGuard saliente sin requerir IP pública fija ni apertura de puertos NAT.

---

# B. PARTE II

## 4. Objetivos

### 4.1 Objetivo General
Diseñar, implementar y validar una arquitectura de defensa en profundidad y respuesta autónoma ante incidentes (SOAR) de costo cero ($0 CLP) denominada **KRONOS SENTINEL**, integrando prevención de intrusiones en kernel, supresión heurística de falsos positivos y notificación interactiva por voz en tiempo real con Inteligencia Artificial hacia los responsables de seguridad (CISO).

### 4.2 Objetivos Específicos
1. **Diseñar e implementar la infraestructura perimetral de red** en pfSense CE 2.9.0 mediante troncal 802.1Q y segmentación en 4 VLANs (Corporativa, DMZ, VoIP y Gestión SecOps).
2. **Configurar el motor de prevención de intrusiones Suricata 7.x en modo Inline IPS** sobre framework Netmap con firmas ET Open y reglas automáticas `dropsid.conf` para el descarte de tráfico malicioso en hardware sin latencia.
3. **Implementar el proxy inverso HAProxy 2.8+ con terminación SSL/TLS** y *Stick-Tables* de control de tasa L7, protegiendo y publicando el servidor web de pruebas vulnerables DVWA en la DMZ.
4. **Desarrollar en Python 3.12 el Motor de Correlación KRONOS** con parser de `eve.json` y algoritmo heurístico AST para suprimir más del 50% de falsos positivos en vectores SQLi y RCE.
5. **Integrar el control atómico de estados y tablas en kernel de FreeBSD** mediante la herramienta `pfctl`, ejecutando la terminación inmediata de conexiones hostiles (`pfctl -k`) y verificación de la tabla `<snort2c>`.
6. **Desplegar la centralita de telefonía Asterisk 20 LTS en Docker** con canal PJSIP y módulo auto-dialer AMI (`Originate`) para el timbrado prioritario al softphone móvil del CISO.
7. **Desarrollar el bridge de audio por WebSocket hacia Google Gemini Live Flash 3.1**, permitiendo la entrega de un debriefing hablado en lenguaje natural y la interlocución táctica en vivo.
8. **Validar la efectividad y rendimiento de la arquitectura completa** mediante matrices de pruebas funcionales de aseguramiento de calidad (QA) y auditoría de tiempos de respuesta (<1.5 s).

---

## 5. Metodología

### 5.1 Descripción de la Metodología
Se utilizará una **Metodología de Ingeniería en Ciclo Iterativo e Incremental**, estructurada en 4 etapas operativas con control de calidad continuo:
1. **Etapa 1 (Diseño y Topología de Red):** Modelamiento de direccionamiento IP, troncales VLAN 802.1Q y hardening base de pfSense CE 2.9.0.
2. **Etapa 2 (Seguridad Perimetral y DMZ):** Despliegue de Suricata Netmap Inline IPS, pfBlockerNG GeoIP, HAProxy SSL y contenedor DVWA.
3. **Etapa 3 (Desarrollo del Motor KRONOS y Telefonía IA):** Programación en Python 3.12 del analizador AST, wrappers `pfctl`, contenedor Asterisk PBX y WebSocket de Gemini Live API.
4. **Etapa 4 (Integración SOAR, QA y Validación de Campo):** Pruebas de inyección SQL en vivo, auditoría de tiempos de latencia, ajuste de umbrales heurísticos y compilación de documentación técnica.

### 5.2 Funciones, Tareas y Responsabilidades del Equipo
* **Bruno Urrea Ortiz (Líder de Ciberseguridad & Motor KRONOS):** Arquitectura global, desarrollo del Motor de Correlación KRONOS (`log_correlator.py`), algoritmo AST de supresión de falsos positivos (`false_positive_filter.py`), control de kernel FreeBSD `pfctl` e integración WebSocket con Gemini Live Flash 3.1.
* **Freddy Vásquez Cortés (Ingeniero de Routing, Switching & VoIP):** Configuración de troncal 802.1Q, direccionamiento de VLANs en pfSense, despliegue de centralita Asterisk 20 LTS en Docker (`pjsip.conf`, `extensions.conf`), auto-dialer AMI (`call_trigger.py`) y enrutamiento Tailscale.
* **Cristóbal Quezada (Administrador de Servicios Web & DMZ):** Configuración de HAProxy 2.8+ con terminación HTTPS 443, diseño de *Stick-Tables* anti-fuzzing L7 y administración del contenedor vulnerable de pruebas DVWA en VLAN 20.
* **Kevin Retamales (Especialista en Hardening, Threat Intelligence & QA):** Hardening de políticas de firewall Zero Trust en pfSense, configuración de pfBlockerNG-devel (MaxMind GeoLite2 y listas FireHOL/Spamhaus) y diseño/ejecución de matrices de prueba QA de extremo a extremo.

---

## 6. Evidencias

| Tipo de Evidencia | Nombre de la Evidencia | Descripción | Justificación |
| :--- | :--- | :--- | :--- |
| **Avance (Fase 1)** | Informe de Definición y Topología de Red | Documento técnico formal con diseño de direccionamiento IP, matriz de VLANs y arquitectura perimetral. | Valida la correcta planificación de la infraestructura L2/L3 y el marco metodológico inicial. |
| **Avance (Fase 2)** | Repositorio Git de Código Fuente e IaC | Repositorio GitHub con código del Motor KRONOS, Dockerfiles de Asterisk/DVWA y configs de pfSense. | Demuestra el avance tangible en desarrollo de software, integración de APIs y automatización de red. |
| **Avance (Fase 2)** | Manuales Técnicos y Mockups en PDF | Manual de configuración de pfSense CE 2.9.0 y Tutorial Paso a Paso de 8 páginas con WebGUI cards. | Acredita la reproducibilidad y rigurosidad técnica de los procedimientos de hardening perimetral. |
| **Final (Fase 3)** | Demostración en Vivo de Intrusión y Respuesta SOAR | Ejecución de inyección SQL en DVWA ➔ Bloqueo en kernel FreeBSD (`snort2c`) ➔ Llamada telefónica de voz con Gemini Live en altavoz. | Evidencia concluyente de la efectividad de la solución y cumplimiento del objetivo general ante la comisión. |
| **Final (Fase 3)** | Matrices de Pruebas de Calidad (QA) y Logs Forenses | Registros EVE JSON de Suricata, salidas de consola `pfctl -t snort2c -T show` y métricas de latencia (<1.5 s). | Respaldan con datos empíricos la supresión de falsos positivos y la robustez del filtrado en kernel. |
| **Final (Fase 3)** | Informe Final Consolidado y Presentación Ejecutiva | Documento consolidado del proyecto y diapositivas de defensa para examen de título. | Entrega formal académica exigida por la pauta de evaluación de Portafolio de Título (APT122). |

---

## 7. Plan de Trabajo

| Competencia | Nombre de Actividad | Descripción de Tarea | Recursos | Duración | Responsable | Observaciones |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Comp. 4 & 8** | A1. Diseño y Setup Base pfSense | Instalación de pfSense CE 2.9.0, configuración WAN/LAN y tuning de hardware offloading para Netmap. | Hipervisor, ISO pfSense CE 2.9.0 | Semanas 1 - 2 | Bruno Urrea / Freddy Vásquez | Crucial desactivar TSO/LRO para estabilidad de Netmap. |
| **Comp. 4** | A2. Segmentación de VLANs 802.1Q | Creación de subredes VLAN 10 (Corp), 20 (DMZ), 30 (VoIP) y 99 (Mgmt) y servidores DHCP locales. | pfSense WebGUI, Switch L2 virtual | Semanas 3 - 4 | Freddy Vásquez | Se aplican reservas MAC estáticas para servidores. |
| **Comp. 7 & 8** | A3. Despliegue de Suricata Inline IPS | Instalación de Suricata 7.x, activación de modo Inline Netmap, reglas ET Open y configuración `dropsid.conf`. | Paquete pfSense Suricata, feeds ET Open | Semanas 5 - 6 | Bruno Urrea / Kevin Retamales | Bloqueo en hardware ring-buffer sin latencia. |
| **Comp. 7 & 8** | A4. Hardening GeoIP con pfBlockerNG | Configuración de cuenta MaxMind Free, bloqueo Top Spammers y feeds FireHOL L1 / Spamhaus DROP. | pfBlockerNG-devel, MaxMind GeoLite2 | Semanas 7 - 8 | Kevin Retamales | Reglas flotantes prioritarias en WAN. |
| **Comp. 7** | A5. Proxy Inverso HAProxy & DVWA | Configuración de Frontend HTTPS VIP 443, SSL Offloading, Stick-Tables anti-fuzzing y contenedor DVWA. | HAProxy package, Docker, DVWA image | Semanas 9 - 10 | Cristóbal Quezada | Aislamiento estricto de DVWA en VLAN 20 DMZ. |
| **Comp. 6 & 8** | A6. Motor de Correlación KRONOS | Programación en Python 3.12 del parser `eve.json`, filtro heurístico AST y wrapper de kernel FreeBSD `pfctl`. | Python 3.12, PyYAML, FreeBSD CLI | Semanas 11 - 12 | Bruno Urrea | Suprime >50% de ruido y ejecuta `pfctl -k`. |
| **Comp. 5** | A7. Centralita VoIP Asterisk PBX | Construcción de imagen Docker Asterisk 20 LTS, configuración de `pjsip.conf`, `extensions.conf` y auto-dialer AMI. | Docker Engine, Asterisk 20 LTS, AMI | Semanas 13 - 14 | Freddy Vásquez | Timbrado prioritario a softphone PJSIP/1001. |
| **Comp. 3 & 5** | A8. Integración Gemini Live Voice | Desarrollo de cliente WebSocket seguro, diseño de System Prompts tácticos y conexión de audio PCM con Asterisk. | Google AI Studio API Key, Python websockets | Semanas 14 - 15 | Bruno Urrea | Diálogo interactivo bidireccional de voz. |
| **Comp. 3 & 4** | A9. Enlace Zero Trust Tailscale | Publicación de subred VoIP `192.168.30.0/24` en Tailscale para softphones móviles remotos sin abrir puertos. | Tailscale package, WireGuard mesh | Semana 15 | Freddy Vásquez | Evade restricciones de CGNAT en sedes. |
| **Comp. 7, 8 & 11** | A10. Pruebas QA, Auditoría & Defensa | Ejecución de matrices de prueba de penetración, medición de tiempos (<1.5 s), manuales PDF y preparación de defensa. | Repositorio GitHub, softphone, ReportLab | Semanas 16 - 18 | Todo el Equipo | Validación final y presentación ante comisión. |

---

## 8. Carta Gantt

| Actividad / Hito | Fase 1 (S1-S4) | | | | Fase 2 (S5-S15) | | | | | | | | | | | Fase 3 (S16-S18) | | |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| | **S1** | **S2** | **S3** | **S4** | **S5** | **S6** | **S7** | **S8** | **S9** | **S10** | **S11** | **S12** | **S13** | **S14** | **S15** | **S16** | **S17** | **S18** |
| **A1. Setup Base pfSense & Tuning** | **X** | **X** | | | | | | | | | | | | | | | | |
| **A2. Segmentación VLANs 802.1Q** | | | **X** | **X** | | | | | | | | | | | | | | |
| **A3. Suricata Inline Netmap IPS** | | | | | **X** | **X** | | | | | | | | | | | | |
| **A4. Hardening GeoIP pfBlockerNG** | | | | | | | **X** | **X** | | | | | | | | | | |
| **A5. HAProxy SSL & Laboratorio DVWA**| | | | | | | | | **X** | **X** | | | | | | | | |
| **A6. Motor de Correlación KRONOS**| | | | | | | | | | | **X** | **X** | | | | | | |
| **A7. Telefonía Asterisk PBX & AMI** | | | | | | | | | | | | | **X** | **X** | | | | |
| **A8. Integración Gemini Live Voice** | | | | | | | | | | | | | | **X** | **X** | | | |
| **A9. Malla Zero Trust Tailscale** | | | | | | | | | | | | | | | **X** | | | |
| **A10. Pruebas QA, Auditoría & Defensa**| | | | | | | | | | | | | | | | **X** | **X** | **X** |
"""

# =============================================================================
# 2. GENERADOR DE WORD (.DOCX) CON FORMATO DUOC UC
# =============================================================================
def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def generate_docx(output_path: str):
    doc = docx.Document()
    
    # Configuración de márgenes
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
    # Encabezado institucional Duoc UC
    header = doc.add_paragraph()
    r_hdr1 = header.add_run("Guía Estudiante - Definición Proyecto APT\nFase 1")
    r_hdr1.font.name = "Arial"
    r_hdr1.font.size = Pt(10)
    r_hdr1.font.bold = True
    r_hdr1.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    
    # Título Principal
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t1 = p_title.add_run("Guía1. Definición Proyecto APT\nAsignatura Portafolio de Título (APT122)\n")
    r_t1.font.name = "Arial"
    r_t1.font.size = Pt(16)
    r_t1.font.bold = True
    r_t1.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    r_sub = p_title.add_run("KRONOS SENTINEL: Autonomous AI-IPS & Real-Time Incident Voice Response SOAR Architecture")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x00, 0x66, 0x99)
    
    # -------------------------------------------------------------
    # SECCIÓN 1: ANTECEDENTES PERSONALES
    # -------------------------------------------------------------
    p_s1 = doc.add_paragraph()
    r_s1 = p_s1.add_run("1. Antecedentes Personales")
    r_s1.font.name = "Arial"
    r_s1.font.size = Pt(12)
    r_s1.font.bold = True
    
    t_pers = doc.add_table(rows=5, cols=2)
    t_pers.alignment = WD_TABLE_ALIGNMENT.CENTER
    pers_data = [
        ("Nombre estudiante", "Bruno Urrea Ortiz"),
        ("Rut", "21.543.637-3"),
        ("Carrera", "Ingeniería en Conectividad y Redes"),
        ("Sede", "San Joaquín"),
        ("Integrantes del Equipo (Grupal)", "• Bruno Urrea Ortiz (Líder de Ciberseguridad, Motor KRONOS y Gemini Live)\n• Freddy Vásquez Cortés (Routing, Switching y Telefonía Asterisk PBX)\n• Cristóbal Quezada (Servicios Web, HAProxy SSL y DMZ DVWA)\n• Kevin Retamales (Hardening Perimetral, pfBlockerNG y QA)")
    ]
    for idx, (k, v) in enumerate(pers_data):
        row = t_pers.rows[idx]
        row.cells[0].text = k
        row.cells[1].text = v
        set_cell_background(row.cells[0], "F0F4F8")
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        for cell in row.cells:
            set_cell_margins(cell)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(9.5)
                    
    doc.add_paragraph()

    # -------------------------------------------------------------
    # SECCIÓN 2: DESCRIPCIÓN PROYECTO APT
    # -------------------------------------------------------------
    p_s2 = doc.add_paragraph()
    r_s2 = p_s2.add_run("2. Descripción Proyecto APT")
    r_s2.font.name = "Arial"
    r_s2.font.size = Pt(12)
    r_s2.font.bold = True
    
    t_desc = doc.add_table(rows=3, cols=2)
    t_desc.alignment = WD_TABLE_ALIGNMENT.CENTER
    desc_data = [
        ("Nombre del proyecto", "KRONOS SENTINEL: Autonomous AI-IPS & Real-Time Incident Voice Response SOAR Architecture"),
        ("Área(s) de desempeño", "• Seguridad de la Información, Ciberseguridad Defensiva y Hardening Perimetral.\n• Infraestructura de Redes Corporativas, Routing y Switching L2/L3 (VLANs 802.1Q).\n• Telecomunicaciones, Telefonía VoIP SIP/PJSIP y Streaming de Audio en Tiempo Real.\n• Automatización, Programación en Python e Integración de Inteligencia Artificial (SOAR)."),
        ("Competencias", "• Competencia 3: Adaptar tecnologías de punta y tendencias emergentes de conectividad.\n• Competencia 4: Controlar y operar redes corporativas de gran tamaño.\n• Competencia 5: Unificar servicios de voz, datos y video.\n• Competencia 6: Automatizar procesos y gestión de plataformas de red.\n• Competencia 7: Gestionar la seguridad de la información frente a vulnerabilidades.\n• Competencia 8: Crear planes de prevención y respuesta a riesgos informáticos.")
    ]
    for idx, (k, v) in enumerate(desc_data):
        row = t_desc.rows[idx]
        row.cells[0].text = k
        row.cells[1].text = v
        set_cell_background(row.cells[0], "F0F4F8")
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        for cell in row.cells:
            set_cell_margins(cell)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(9.5)
                    
    doc.add_paragraph()

    # -------------------------------------------------------------
    # SECCIÓN 3: FUNDAMENTACIÓN PROYECTO APT
    # -------------------------------------------------------------
    p_s3 = doc.add_paragraph()
    r_s3 = p_s3.add_run("3. Fundamentación Proyecto APT")
    r_s3.font.name = "Arial"
    r_s3.font.size = Pt(12)
    r_s3.font.bold = True
    
    t_fund = doc.add_table(rows=5, cols=2)
    t_fund.alignment = WD_TABLE_ALIGNMENT.CENTER
    fund_data = [
        ("Relevancia del proyecto APT", "El proyecto resuelve dos fallas críticas en los SOC modernos: la sobrecarga paralizante de más de un 50% de falsos positivos en firewalls y el colapso cognitivo del operador humano bajo presión durante una brecha activa. KRONOS SENTINEL aporta una solución SOAR de Costo Cero ($0 CLP) que desacopla la contención técnica en kernel de FreeBSD (<100 ms) de la comunicación estratégica mediante llamadas con IA conversacional (<1.5 s)."),
        ("Descripción del Proyecto APT", "Arquitectura de defensa en profundidad compuesta por: 1) Firewall pfSense CE 2.9.0 con Suricata Inline Netmap IPS y pfBlockerNG GeoIP; 2) DMZ con HAProxy SSL protegiendo el laboratorio vulnerable DVWA; 3) Motor de Correlación KRONOS (Python 3.12) con análisis heurístico AST y control en kernel con pfctl (kill states y tabla snort2c); y 4) Centralita Asterisk 20 LTS con auto-dialer AMI y Google Gemini Live Flash 3.1 para debriefing interactivo por voz."),
        ("Pertinencia del proyecto con el perfil de egreso", "Integra armónicamente las 4 áreas troncales de Ingeniería en Conectividad y Redes: Routing & Switching L2/L3 (VLANs 802.1Q), Ciberseguridad Perimetral (Hardening, IPS, Zero Trust), Telefonía VoIP (Asterisk SIP/PJSIP) y Automatización (Python, IPC, IA Generativa)."),
        ("Relación con los intereses profesionales", "Se alinea con mi especialización como Ingeniero de Ciberseguridad / Arquitecto SecOps y SOAR, consolidando la experiencia práctica liderando el equipo de competiciones CTF DevSec y proyectos de mitigación perimetral."),
        ("Factibilidad de desarrollo del Proyecto APT", "Factible al 100%: 1) 18 semanas de planificación semestral; 2) 72h lectivas + 144h autónomas; 3) Materiales con Costo Cero ($0 CLP) basados en software libre y capas comunitarias gratuitas; 4) Infraestructura de virtualización Proxmox/VMware; 5) Superación de restricciones CGNAT mediante túnel Zero Trust Mesh con Tailscale Subnet Router.")
    ]
    for idx, (k, v) in enumerate(fund_data):
        row = t_fund.rows[idx]
        row.cells[0].text = k
        row.cells[1].text = v
        set_cell_background(row.cells[0], "F0F4F8")
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        for cell in row.cells:
            set_cell_margins(cell)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(9.5)

    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN 4: OBJETIVOS
    # -------------------------------------------------------------
    p_s4 = doc.add_paragraph()
    r_s4 = p_s4.add_run("B. PARTE II\n4. Objetivos")
    r_s4.font.name = "Arial"
    r_s4.font.size = Pt(12)
    r_s4.font.bold = True
    
    t_obj = doc.add_table(rows=2, cols=2)
    t_obj.alignment = WD_TABLE_ALIGNMENT.CENTER
    obj_data = [
        ("Objetivo general", "Diseñar, implementar y validar una arquitectura de defensa en profundidad y respuesta autónoma ante incidentes (SOAR) de costo cero ($0 CLP) denominada KRONOS SENTINEL, integrando prevención de intrusiones en kernel, supresión heurística de falsos positivos e interlocución telefónica interactiva por voz en tiempo real con Inteligencia Artificial hacia los responsables de seguridad (CISO)."),
        ("Objetivos específicos", "1. Diseñar e implementar la infraestructura perimetral en pfSense CE 2.9.0 con segmentación en 4 VLANs 802.1Q.\n2. Configurar Suricata 7.x en modo Inline IPS (Netmap) con reglas dropsid.conf para descarte en hardware.\n3. Implementar HAProxy 2.8+ SSL con Stick-Tables anti-fuzzing L7 protegiendo el entorno DVWA en DMZ.\n4. Desarrollar en Python 3.12 el Motor de Correlación KRONOS con análisis sintáctico AST de SQLi/RCE suprimiendo >50% de falsos positivos.\n5. Integrar el control en kernel de FreeBSD con pfctl para terminación de estados (pfctl -k) y verificación de tabla snort2c.\n6. Desplegar Asterisk 20 LTS en Docker con canal PJSIP y auto-dialer AMI hacia el CISO.\n7. Desarrollar el bridge WebSocket hacia Google Gemini Live Flash 3.1 para debriefing interactivo por voz.\n8. Validar la efectividad y rendimiento integral mediante matrices de aseguramiento de calidad (QA).")
    ]
    for idx, (k, v) in enumerate(obj_data):
        row = t_obj.rows[idx]
        row.cells[0].text = k
        row.cells[1].text = v
        set_cell_background(row.cells[0], "F0F4F8")
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        for cell in row.cells:
            set_cell_margins(cell)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(9.5)

    doc.add_paragraph()

    # -------------------------------------------------------------
    # SECCIÓN 5: METODOLOGÍA
    # -------------------------------------------------------------
    p_s5 = doc.add_paragraph()
    r_s5 = p_s5.add_run("5. Metodología")
    r_s5.font.name = "Arial"
    r_s5.font.size = Pt(12)
    r_s5.font.bold = True
    
    t_met = doc.add_table(rows=1, cols=1)
    t_met.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_met = t_met.rows[0].cells[0]
    cell_met.text = (
        "Descripción de la Metodología:\n"
        "Se aplicará una Metodología de Ingeniería en Ciclo Iterativo e Incremental en 4 fases operativas con validación continua QA:\n"
        "• Fase 1: Diseño y Topología de Red (VLANs 802.1Q, direccionamiento IP y hardening pfSense CE 2.9.0).\n"
        "• Fase 2: Seguridad Perimetral y DMZ (Suricata Inline Netmap IPS, pfBlockerNG GeoIP, HAProxy SSL y DVWA).\n"
        "• Fase 3: Motor de Correlación KRONOS y Telefonía IA (Python 3.12 AST parser, pfctl kernel control, Asterisk PBX y Gemini Live API).\n"
        "• Fase 4: Integración SOAR, Pruebas QA y Auditoría (Simulaciones SQLi en vivo, medición de latencia <1.5s y documentación técnica).\n\n"
        "Distribución de Funciones y Tareas del Equipo:\n"
        "• Bruno Urrea Ortiz: Líder de Ciberseguridad, desarrollo del Motor de Correlación KRONOS, algoritmo AST anti-ruido, control en kernel pfctl y cliente WebSocket Gemini Live.\n"
        "• Freddy Vásquez Cortés: Ingeniería de Routing, segmentación VLAN 802.1Q, centralita Asterisk 20 LTS en Docker, auto-dialer AMI y enlace Tailscale.\n"
        "• Cristóbal Quezada: Administración de Servicios Web, configuración HAProxy 2.8+ SSL, Stick-Tables de rate-limiting y laboratorio web DVWA en DMZ.\n"
        "• Kevin Retamales: Hardening de firewall pfSense Zero Trust, pfBlockerNG-devel (MaxMind GeoIP y feeds FireHOL/Spamhaus) y matrices de control de calidad QA."
    )
    set_cell_margins(cell_met)
    for p in cell_met.paragraphs:
        for r in p.runs:
            r.font.name = "Arial"
            r.font.size = Pt(9.5)

    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN 6: EVIDENCIAS
    # -------------------------------------------------------------
    p_s6 = doc.add_paragraph()
    r_s6 = p_s6.add_run("6. Evidencias")
    r_s6.font.name = "Arial"
    r_s6.font.size = Pt(12)
    r_s6.font.bold = True
    
    t_evi = doc.add_table(rows=7, cols=4)
    t_evi.alignment = WD_TABLE_ALIGNMENT.CENTER
    evi_headers = ["Tipo de evidencia", "Nombre de la evidencia", "Descripción", "Justificación"]
    for c_idx, h in enumerate(evi_headers):
        t_evi.rows[0].cells[c_idx].text = h
        set_cell_background(t_evi.rows[0].cells[c_idx], "003366")
        t_evi.rows[0].cells[c_idx].paragraphs[0].runs[0].font.bold = True
        t_evi.rows[0].cells[c_idx].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    evi_rows = [
        ("Avance (F1)", "Informe de Definición y Topología", "Documento técnico formal con diseño L2/L3 y matriz de VLANs.", "Valida la correcta planificación de la infraestructura."),
        ("Avance (F2)", "Repositorio Git de Código e IaC", "GitHub con código del Motor KRONOS, Dockerfiles y configs pfSense.", "Demuestra el avance tangible en desarrollo y automatización."),
        ("Avance (F2)", "Manuales Técnicos y Mockups PDF", "Manual pfSense CE 2.9.0 y Tutorial Paso a Paso con WebGUI cards.", "Acredita la reproducibilidad y rigor técnico de las configuraciones."),
        ("Final (F3)", "Demostración en Vivo SOAR", "Inyección SQL en DVWA ➔ Bloqueo kernel snort2c ➔ Llamada Gemini Live.", "Evidencia concluyente del cumplimiento del objetivo general."),
        ("Final (F3)", "Matrices QA y Logs Forenses", "Registros EVE JSON, salidas pfctl y métricas de latencia (<1.5s).", "Respaldan con datos empíricos la supresión de ruido y robustez."),
        ("Final (F3)", "Informe Final y Presentación", "Documento consolidado del proyecto y diapositivas de defensa.", "Entrega formal exigida para la titulación en Portafolio APT122.")
    ]
    for r_idx, row_data in enumerate(evi_rows):
        row = t_evi.rows[r_idx+1]
        for c_idx, val in enumerate(row_data):
            row.cells[c_idx].text = val
            if r_idx % 2 == 1:
                set_cell_background(row.cells[c_idx], "F7FAFC")
            for p in row.cells[c_idx].paragraphs:
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(8.5)
            set_cell_margins(row.cells[c_idx], top=60, bottom=60, left=100, right=100)

    doc.add_paragraph()

    # -------------------------------------------------------------
    # SECCIÓN 7: PLAN DE TRABAJO
    # -------------------------------------------------------------
    p_s7 = doc.add_paragraph()
    r_s7 = p_s7.add_run("7. Plan de Trabajo")
    r_s7.font.name = "Arial"
    r_s7.font.size = Pt(12)
    r_s7.font.bold = True
    
    t_plan = doc.add_table(rows=11, cols=7)
    t_plan.alignment = WD_TABLE_ALIGNMENT.CENTER
    plan_headers = ["Competencia", "Nombre Actividad", "Descripción", "Recursos", "Duración", "Responsable", "Observaciones"]
    for c_idx, h in enumerate(plan_headers):
        t_plan.rows[0].cells[c_idx].text = h
        set_cell_background(t_plan.rows[0].cells[c_idx], "003366")
        t_plan.rows[0].cells[c_idx].paragraphs[0].runs[0].font.bold = True
        t_plan.rows[0].cells[c_idx].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    plan_rows = [
        ("Comp. 4 & 8", "A1. Setup pfSense", "Instalación pfSense 2.9.0, WAN/LAN y tuning de hardware offloading.", "pfSense ISO", "S1 - S2", "Bruno / Freddy", "Desactivar TSO/LRO para Netmap."),
        ("Comp. 4", "A2. VLANs 802.1Q", "Creación de VLANs 10, 20, 30, 99 y servidores DHCP.", "pfSense WebGUI", "S3 - S4", "Freddy Vásquez", "Mapeos MAC estáticos para servers."),
        ("Comp. 7 & 8", "A3. Suricata IPS", "Suricata 7.x Inline Netmap, ET Open y dropsid.conf.", "Suricata pkg", "S5 - S6", "Bruno / Kevin", "Descarte en hardware ring-buffer."),
        ("Comp. 7 & 8", "A4. GeoIP pfBlocker", "MaxMind Free, Top Spammers y feeds FireHOL L1/Spamhaus.", "pfBlockerNG", "S7 - S8", "Kevin Retamales", "Reglas flotantes prioritarias."),
        ("Comp. 7", "A5. HAProxy & DVWA", "HAProxy SSL 443, Stick-Tables anti-fuzzing y DVWA Docker.", "HAProxy, Docker", "S9 - S10", "Cristóbal Q.", "Aislamiento DMZ en VLAN 20."),
        ("Comp. 6 & 8", "A6. Motor KRONOS", "Python 3.12 AST parser, eve.json ingesta y wrapper pfctl.", "Python 3.12", "S11 - S12", "Bruno Urrea", "Suprime >50% ruido y kill states."),
        ("Comp. 5", "A7. Asterisk PBX", "Docker Asterisk 20 LTS, pjsip.conf y auto-dialer AMI.", "Asterisk 20", "S13 - S14", "Freddy Vásquez", "Timbrado a softphone PJSIP/1001."),
        ("Comp. 3 & 5", "A8. Gemini Live", "WebSocket seguro, System Prompts y audio bridge.", "Gemini Live API", "S14 - S15", "Bruno Urrea", "Debriefing hablado interactivo."),
        ("Comp. 3 & 4", "A9. Malla Tailscale", "Publicación subred 192.168.30.0/24 en Tailscale Mesh.", "Tailscale pkg", "S15", "Freddy Vásquez", "Evade restricciones de CGNAT."),
        ("Comp. 7, 8, 11", "A10. QA & Defensa", "Pruebas de estrés, manuales PDF y preparación defensa.", "ReportLab, Git", "S16 - S18", "Todo el Equipo", "Demostración en vivo aprobada.")
    ]
    for r_idx, row_data in enumerate(plan_rows):
        row = t_plan.rows[r_idx+1]
        for c_idx, val in enumerate(row_data):
            row.cells[c_idx].text = val
            if r_idx % 2 == 1:
                set_cell_background(row.cells[c_idx], "F7FAFC")
            for p in row.cells[c_idx].paragraphs:
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(8)
            set_cell_margins(row.cells[c_idx], top=50, bottom=50, left=60, right=60)

    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN 8: CARTA GANTT
    # -------------------------------------------------------------
    p_s8 = doc.add_paragraph()
    r_s8 = p_s8.add_run("8. Carta Gantt (18 Semanas Académicas)")
    r_s8.font.name = "Arial"
    r_s8.font.size = Pt(12)
    r_s8.font.bold = True
    
    t_gantt = doc.add_table(rows=11, cols=19)
    t_gantt.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Headers
    t_gantt.rows[0].cells[0].text = "Actividad"
    set_cell_background(t_gantt.rows[0].cells[0], "003366")
    t_gantt.rows[0].cells[0].paragraphs[0].runs[0].font.bold = True
    t_gantt.rows[0].cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    
    for s in range(1, 19):
        cell = t_gantt.rows[0].cells[s]
        cell.text = f"S{s}"
        set_cell_background(cell, "003366")
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell.paragraphs[0].runs[0].font.size = Pt(7)

    gantt_activities = [
        ("A1. Setup pfSense Base", [1, 2]),
        ("A2. Segmentación VLANs", [3, 4]),
        ("A3. Suricata Inline IPS", [5, 6]),
        ("A4. GeoIP pfBlockerNG", [7, 8]),
        ("A5. HAProxy SSL & DVWA", [9, 10]),
        ("A6. Motor KRONOS pfctl", [11, 12]),
        ("A7. Asterisk PBX & AMI", [13, 14]),
        ("A8. Gemini Live Voice", [14, 15]),
        ("A9. Malla Tailscale", [15]),
        ("A10. Pruebas QA & Defensa", [16, 17, 18])
    ]
    for r_idx, (act_name, weeks) in enumerate(gantt_activities):
        row = t_gantt.rows[r_idx+1]
        row.cells[0].text = act_name
        row.cells[0].paragraphs[0].runs[0].font.size = Pt(7.5)
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        set_cell_margins(row.cells[0], top=30, bottom=30, left=50, right=50)
        
        for w in range(1, 19):
            cell = row.cells[w]
            set_cell_margins(cell, top=30, bottom=30, left=20, right=20)
            if w in weeks:
                cell.text = "X"
                set_cell_background(cell, "006699")
                cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                cell.paragraphs[0].runs[0].font.bold = True
                cell.paragraphs[0].runs[0].font.size = Pt(7)
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                cell.text = ""

    doc.save(output_path)
    print(f"[OK] Word DOCX generated: {output_path}")

# =============================================================================
# 3. GENERADOR DE PDF OFICIAL CON REPORTLAB
# =============================================================================
BG_COLOR = colors.HexColor("#070A11")
CYAN_ACCENT = colors.HexColor("#00E5FF")
TEXT_LIGHT = colors.HexColor("#E2E8F0")
TEXT_MUTED = colors.HexColor("#64748B")
TEXT_HEADING = colors.HexColor("#F8FAFC")
BORDER_COLOR = colors.HexColor("#1E293B")
CARD_HEADER_BG = colors.HexColor("#111827")
CARD_BODY_BG = colors.HexColor("#0B1120")

class DuocCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        # Header
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(CYAN_ACCENT)
        self.drawString(40, 762, "DUOC UC — SAN JOAQUÍN")
        
        self.setFont("Helvetica", 7.5)
        self.setFillColor(TEXT_MUTED)
        self.drawString(160, 762, "// Guía1. Definición Proyecto APT (Fase 1 - APT122)")
        
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(TEXT_LIGHT)
        self.drawRightString(572, 762, "KRONOS SENTINEL")
        
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(40, 754, 572, 754)
        
        # Footer
        self.setFont("Helvetica", 7.5)
        self.setFillColor(TEXT_MUTED)
        self.drawString(40, 28, "PORTAFOLIO DE TÍTULO (APT122) • ESTUDIANTE: BRUNO URREA ORTIZ")
        
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(CYAN_ACCENT)
        self.drawRightString(572, 28, f"PÁGINA {self._pageNumber} / {page_count}")
        
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(40, 38, 572, 38)
        self.restoreState()

def draw_pdf_bg(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFillColor(BG_COLOR)
    canvas_obj.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=True, stroke=False)
    canvas_obj.restoreState()

def generate_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=TEXT_HEADING,
        alignment=1,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=CYAN_ACCENT,
        alignment=1,
        spaceAfter=4
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=CYAN_ACCENT,
        spaceBefore=4,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=TEXT_LIGHT,
        spaceAfter=2
    )

    story = []

    # =========================================================================
    # PÁGINA 1: PARTE I (ANTECEDENTES, DESCRIPCIÓN & FUNDAMENTACIÓN)
    # =========================================================================
    story.append(Paragraph("GUÍA 1: DEFINICIÓN PROYECTO APT — FASE 1", title_style))
    story.append(Paragraph("PORTAFOLIO DE TÍTULO (APT122) • INGENIERÍA EN CONECTIVIDAD Y REDES", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=4))

    story.append(Paragraph("1. ANTECEDENTES PERSONALES", h1_style))
    pers_data = [
        [Paragraph("<b>Nombre estudiante</b>", body_style), Paragraph("Bruno Urrea Ortiz", body_style)],
        [Paragraph("<b>Rut</b>", body_style), Paragraph("21.543.637-3", body_style)],
        [Paragraph("<b>Carrera / Sede</b>", body_style), Paragraph("Ingeniería en Conectividad y Redes / San Joaquín", body_style)],
        [Paragraph("<b>Equipo de Trabajo</b>", body_style), Paragraph("• Bruno Urrea Ortiz (Líder Ciberseguridad) • Freddy Vásquez (Routing & VoIP)<br/>• Cristóbal Quezada (Web & DMZ) • Kevin Retamales (Hardening & QA)", body_style)]
    ]
    t_p = Table(pers_data, colWidths=[130, 402])
    t_p.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), CARD_HEADER_BG),
        ('BACKGROUND', (1,0), (1,-1), CARD_BODY_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#334155")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_p)
    story.append(Spacer(1, 3))

    story.append(Paragraph("2. DESCRIPCIÓN DEL PROYECTO APT", h1_style))
    desc_data = [
        [Paragraph("<b>Nombre Proyecto</b>", body_style), Paragraph("<b>KRONOS SENTINEL:</b> Autonomous AI-IPS & Real-Time Incident Voice Response SOAR Architecture", body_style)],
        [Paragraph("<b>Áreas de Desempeño</b>", body_style), Paragraph("Ciberseguridad Perimetral, Routing/Switching L2/L3 (VLANs 802.1Q), Telefonía VoIP SIP/PJSIP y Automatización con IA.", body_style)],
        [Paragraph("<b>Competencias Clave</b>", body_style), Paragraph("Comp. 3 (Tendencias de conectividad) • Comp. 4 (Redes corporativas) • Comp. 5 (Voz y datos) • Comp. 6 (Automatización) • Comp. 7 (Gestión vulnerabilidades) • Comp. 8 (Prevención riesgos).", body_style)]
    ]
    t_d = Table(desc_data, colWidths=[130, 402])
    t_d.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), CARD_HEADER_BG),
        ('BACKGROUND', (1,0), (1,-1), CARD_BODY_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#334155")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_d)
    story.append(Spacer(1, 3))

    story.append(Paragraph("3. FUNDAMENTACIÓN PROYECTO APT", h1_style))
    fund_data = [
        [Paragraph("<b>Relevancia Laboral</b>", body_style), Paragraph("Resuelve la sobrecarga de >50% de falsos positivos en firewalls y el colapso cognitivo del operador humano bajo presión, conteniendo en kernel (<100ms) e informando al CISO por voz interactiva (<1.5s).", body_style)],
        [Paragraph("<b>Descripción Técnica</b>", body_style), Paragraph("pfSense 2.9.0 + Suricata Inline Netmap + HAProxy SSL + Motor KRONOS (Python AST parser / pfctl kill states) + Asterisk PBX AMI + Google Gemini Live Flash 3.1 ($0 CLP).", body_style)],
        [Paragraph("<b>Perfil de Egreso</b>", body_style), Paragraph("Conecta de forma sinérgica la infraestructura de redes L2/L3, el hardening perimetral, la telefonía VoIP y el desarrollo de automatizaciones avanzadas.", body_style)],
        [Paragraph("<b>Factibilidad $0 CLP</b>", body_style), Paragraph("18 semanas, 72h lectivas + 144h autónomas. Software 100% libre y capas gratuitas. Evasión de CGNAT mediante Tailscale Subnet Router.", body_style)]
    ]
    t_f = Table(fund_data, colWidths=[130, 402])
    t_f.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), CARD_HEADER_BG),
        ('BACKGROUND', (1,0), (1,-1), CARD_BODY_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#334155")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_f)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: PARTE II (OBJETIVOS, METODOLOGÍA, EVIDENCIAS & GANTT)
    # =========================================================================
    story.append(Paragraph("4. OBJETIVOS GENERAL Y ESPECÍFICOS", h1_style))
    obj_data = [
        [Paragraph("<b>Objetivo General</b>", body_style), Paragraph("Diseñar, implementar y validar la arquitectura KRONOS SENTINEL de costo cero ($0 CLP), integrando prevención de intrusiones en kernel, supresión heurística de falsos positivos y notificación interactiva por voz en tiempo real con Inteligencia Artificial hacia el CISO.", body_style)],
        [Paragraph("<b>Objetivos Específicos</b>", body_style), Paragraph("1. Infraestructura perimetral pfSense CE 2.9.0 con 4 VLANs 802.1Q.<br/>2. Suricata 7.x Inline Netmap IPS y reglas dropsid.conf sin latencia.<br/>3. HAProxy 2.8+ SSL con Stick-Tables anti-fuzzing protegiendo DVWA en DMZ.<br/>4. Motor de Correlación KRONOS en Python 3.12 con análisis AST anti-ruido.<br/>5. Control atómico en kernel FreeBSD con pfctl (kill states y tabla snort2c).<br/>6. Asterisk 20 LTS en Docker con auto-dialer AMI hacia PJSIP/1001.<br/>7. Bridge WebSocket hacia Google Gemini Live Flash 3.1 para debriefing interactivo.<br/>8. Validación empírica mediante matrices de pruebas QA (<1.5 s).", body_style)]
    ]
    t_o = Table(obj_data, colWidths=[130, 402])
    t_o.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), CARD_HEADER_BG),
        ('BACKGROUND', (1,0), (1,-1), CARD_BODY_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#334155")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_o)
    story.append(Spacer(1, 3))

    story.append(Paragraph("5. METODOLOGÍA Y FUNCIONES DEL EQUIPO", h1_style))
    story.append(Paragraph("Metodología de Ingeniería en Ciclo Iterativo e Incremental (4 Fases: Diseño L2/L3 ➔ Seguridad Perimetral ➔ Motor KRONOS & VoIP IA ➔ Integración SOAR & QA).<br/><b>Funciones:</b> • <b>Bruno Urrea:</b> Líder Ciberseguridad, Motor KRONOS, pfctl y Gemini Live. • <b>Freddy Vásquez:</b> Routing, VLANs, Asterisk y Tailscale. • <b>Cristóbal Quezada:</b> HAProxy SSL y DMZ DVWA. • <b>Kevin Retamales:</b> Hardening, GeoIP pfBlockerNG y QA.", body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("6. PLAN DE TRABAJO & CARTA GANTT RESUMIDA (18 SEMANAS)", h1_style))
    gantt_data = [
        [Paragraph("<b>Actividad / Entregable</b>", body_style), Paragraph("<b>Resp.</b>", body_style), Paragraph("<b>Fase 1 (S1-S4)</b>", body_style), Paragraph("<b>Fase 2 (S5-S15)</b>", body_style), Paragraph("<b>Fase 3 (S16-S18)</b>", body_style)],
        [Paragraph("A1-A2. Setup pfSense & VLANs 802.1Q", body_style), Paragraph("Bruno/Freddy", body_style), Paragraph("<b>S1 - S4</b>", body_style), Paragraph("-", body_style), Paragraph("-", body_style)],
        [Paragraph("A3-A4. Suricata Netmap & pfBlocker GeoIP", body_style), Paragraph("Bruno/Kevin", body_style), Paragraph("-", body_style), Paragraph("<b>S5 - S8</b>", body_style), Paragraph("-", body_style)],
        [Paragraph("A5. HAProxy SSL & Laboratorio DVWA", body_style), Paragraph("Cristóbal", body_style), Paragraph("-", body_style), Paragraph("<b>S9 - S10</b>", body_style), Paragraph("-", body_style)],
        [Paragraph("A6-A7. Motor KRONOS, pfctl & Asterisk PBX", body_style), Paragraph("Bruno/Freddy", body_style), Paragraph("-", body_style), Paragraph("<b>S11 - S14</b>", body_style), Paragraph("-", body_style)],
        [Paragraph("A8-A9. Gemini Live Voice & Tailscale Mesh", body_style), Paragraph("Bruno/Freddy", body_style), Paragraph("-", body_style), Paragraph("<b>S14 - S15</b>", body_style), Paragraph("-", body_style)],
        [Paragraph("A10. Pruebas QA, Auditoría & Defensa", body_style), Paragraph("Todo el Equipo", body_style), Paragraph("-", body_style), Paragraph("-", body_style), Paragraph("<b>S16 - S18</b>", body_style)]
    ]
    t_g = Table(gantt_data, colWidths=[180, 80, 90, 90, 92])
    t_g.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HEADER_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BODY_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#334155")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_g)

    doc.build(story, canvasmaker=DuocCanvas, onFirstPage=draw_pdf_bg, onLaterPages=draw_pdf_bg)
    print(f"[OK] PDF generated: {output_path}")

if __name__ == "__main__":
    out_dir = "docs/Fase_1_Definicion_Proyecto_APT"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Guardar Markdown
    md_file = os.path.join(out_dir, "Guia1_Definicion_Proyecto_APT_Fase1_Bruno_Urrea.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(MARKDOWN_CONTENT)
    print(f"[OK] Markdown generated: {md_file}")
    
    # 2. Guardar Word DOCX
    docx_file = os.path.join(out_dir, "Guia1_Definicion_Proyecto_APT_Fase1_Bruno_Urrea.docx")
    generate_docx(docx_file)
    
    # 3. Guardar PDF
    pdf_file = os.path.join(out_dir, "Guia1_Definicion_Proyecto_APT_Fase1_Bruno_Urrea.pdf")
    generate_pdf(pdf_file)
