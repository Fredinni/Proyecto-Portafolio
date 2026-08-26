#!/usr/bin/env python3
"""
KRONOS SENTINEL - Roles & General Knowledge Base Master PDF Generator
Author: Bruno Urrea Ortiz (Portafolio de Título APT122 - Duoc UC)
Covers: 4 Roles, 10 Technologies, Human Factor Innovation & Live Defense Script
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image, Preformatted
)
from reportlab.pdfgen import canvas

BG_COLOR = colors.HexColor("#070A11")
CYAN_ACCENT = colors.HexColor("#00E5FF")
CRIMSON_BADGE = colors.HexColor("#F43F5E")
BORDER_COLOR = colors.HexColor("#1E293B")
BORDER_MUTED = colors.HexColor("#334155")
TEXT_MUTED = colors.HexColor("#64748B")
TEXT_LIGHT = colors.HexColor("#E2E8F0")
TEXT_HEADING = colors.HexColor("#F8FAFC")
CODE_BG = colors.HexColor("#0A0F1D")
CODE_TEXT = colors.HexColor("#38BDF8")

CARD_HEADER_BG = colors.HexColor("#111827")
CARD_BODY_BG = colors.HexColor("#0B1120")

class NumberedCanvas(canvas.Canvas):
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
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(CYAN_ACCENT)
            self.drawString(40, 762, "KRONOS SENTINEL")
            
            self.setFont("Helvetica", 7.5)
            self.setFillColor(TEXT_MUTED)
            self.drawString(130, 762, "//  Base de Conocimiento General & Asignación de Roles")
            
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(TEXT_LIGHT)
            self.drawRightString(572, 762, "DUOC UC SAN JOAQUÍN")
            
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(40, 754, 572, 754)
            
        self.setFont("Helvetica", 7.5)
        self.setFillColor(TEXT_MUTED)
        self.drawString(40, 28, "PORTAFOLIO DE TÍTULO (APT122) • ARQUITECTURA DE COSTO CERO ($0 CLP)")
        
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(CYAN_ACCENT)
        self.drawRightString(572, 28, f"PÁGINA {self._pageNumber} / {page_count}")
        
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(40, 38, 572, 38)
        self.restoreState()

def draw_background(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFillColor(BG_COLOR)
    canvas_obj.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=True, stroke=False)
    canvas_obj.restoreState()

def build_pdf(output_filename: str):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=TEXT_HEADING,
        alignment=1,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=CYAN_ACCENT,
        alignment=1,
        spaceAfter=3
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=TEXT_MUTED,
        alignment=1,
        spaceAfter=6
    )

    h1_style = ParagraphStyle(
        'H1Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=CYAN_ACCENT,
        spaceBefore=4,
        spaceAfter=2
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=TEXT_HEADING,
        spaceBefore=3,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=TEXT_LIGHT,
        spaceAfter=2
    )

    callout_style = ParagraphStyle(
        'CalloutStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=CRIMSON_BADGE,
        spaceBefore=2,
        spaceAfter=2
    )

    story = []

    # =========================================================================
    # PÁGINA 1: PORTADA & INNOVACIÓN DEL FACTOR HUMANO
    # =========================================================================
    logo_path = "assets/sentinel_shield_logo.png"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=70, height=70))
        story.append(Spacer(1, 2))

    story.append(Paragraph("BASE DE CONOCIMIENTO GENERAL Y ASIGNACIÓN DE ROLES", title_style))
    story.append(Paragraph("DISRUPCIÓN DEL FACTOR HUMANO, MATRIZ TECNOLÓGICA Y PLAYBOOK DE DEFENSA", subtitle_style))
    story.append(Paragraph("<b>Institución:</b> Duoc UC Sede San Joaquín • <b>Portafolio de Título APT122</b> • Arquitectura $0 CLP", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=4))

    story.append(Paragraph("1. LA INNOVACIÓN DISRUPTIVA: REMOCIÓN DEL ESLABÓN MÁS DÉBIL (EL FACTOR HUMANO)", h1_style))
    story.append(Paragraph("En un Centro de Operaciones de Seguridad (SOC) convencional, ante una intrusión crítica masiva, el operador de guardia experimenta un colapso cognitivo y visión de túnel bajo presión extrema. Se enfrenta a un dilema paralizante: <b>¿Investiga y bloquea la IP en el firewall o llama por teléfono al CISO para alertar?</b> Al intentar hacer ambas cosas a la vez, se comenten errores de digitación, se olvidan datos forenses y el incidente escala.", body_style))
    story.append(Paragraph("<b>KRONOS SENTINEL</b> resuelve este cuello de botella desacoplando ambas tareas de forma autónoma:", callout_style))
    story.append(Paragraph("• <b>Vía 1 (Contención Técnica en Microsegundos):</b> El motor en kernel de FreeBSD (pfctl / snort2c) y Suricata Netmap ejecutan el bloqueo atómico sin intervención humana.<br/>• <b>Vía 2 (Comunicación Táctica Inmediata):</b> El auto-dialer Asterisk PBX y Google Gemini Live Flash 3.1 llaman por teléfono al CISO y entregan un debriefing hablado en tiempo real, sin titubeos ni bloqueos emocionales.", body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. MATRIZ MAESTRA DE LAS 10 TECNOLOGÍAS DEL SISTEMA ($0 CLP)", h1_style))
    tech_data = [
        [Paragraph("<b>Tecnología</b>", body_style), Paragraph("<b>Licencia</b>", body_style), Paragraph("<b>Justificación y Rol Táctico en KRONOS SENTINEL</b>", body_style)],
        [Paragraph("pfSense CE 2.9.0", body_style), Paragraph("Open Source", body_style), Paragraph("Firewall perimetral base, soporte VLAN 802.1Q y gestión de paquetes.", body_style)],
        [Paragraph("FreeBSD pfctl / snort2c", body_style), Paragraph("BSD ($0)", body_style), Paragraph("Filtrado atómico en kernel de FreeBSD con tabla dinámica en RAM.", body_style)],
        [Paragraph("Suricata 7.x (Netmap)", body_style), Paragraph("GPLv2 ($0)", body_style), Paragraph("Inspección profunda multihilo e intercepción Inline IPS en ring-buffers.", body_style)],
        [Paragraph("ET Open Rules", body_style), Paragraph("Free Tier", body_style), Paragraph("Más de 30,000 firmas comunitarias para SQLi, exploits web y shellcodes.", body_style)],
        [Paragraph("pfBlockerNG-devel", body_style), Paragraph("Open Source", body_style), Paragraph("Reglas flotantes perimetrales prioritarias para GeoIP y listas C2.", body_style)],
        [Paragraph("MaxMind GeoLite2", body_style), Paragraph("Free Tier", body_style), Paragraph("Base de geolocalización IP para reporte verbal de país al CISO.", body_style)],
        [Paragraph("HAProxy 2.8+ SSL", body_style), Paragraph("GPLv2 ($0)", body_style), Paragraph("Terminación SSL 443, rate limiting y stick-tables anti-fuzzing L7.", body_style)],
        [Paragraph("Asterisk 20 LTS", body_style), Paragraph("GPLv2 ($0)", body_style), Paragraph("Telefonía SIP PJSIP y auto-dialer instantáneo vía comandos AMI.", body_style)],
        [Paragraph("Gemini Live Flash 3.1", body_style), Paragraph("Free Tier", body_style), Paragraph("Streaming de audio bidireccional por WebSocket para diálogo interactivo.", body_style)],
        [Paragraph("Tailscale Subnet Router", body_style), Paragraph("Free Tier", body_style), Paragraph("Malla WireGuard Zero Trust para conectar softphone móvil sin abrir puertos.", body_style)],
    ]
    t_tech = Table(tech_data, colWidths=[110, 65, 357])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HEADER_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BODY_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_MUTED),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tech)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: GUÍA DE ROLES 1 & 2 (BRUNO URREA Y FREDDY VÁSQUEZ)
    # =========================================================================
    story.append(Paragraph("3. GUÍA DE ROLES TÉCNICOS Y RESPONSABILIDADES", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=4))

    story.append(Paragraph("ROL 1: BRUNO URREA ORTIZ — LÍDER DE CIBERSEGURIDAD, MOTOR PFCTL & GEMINI LIVE", h2_style))
    story.append(Paragraph("• <b>Responsabilidades:</b> Arquitectura global, motor de correlación en Python 3.12 (`log_correlator.py`), algoritmo de supresión de falsos positivos con análisis sintáctico AST (`false_positive_filter.py`), verificación en kernel (`pfctl_wrapper.py`) e integración WebSocket con Gemini Live Flash 3.1.<br/>• <b>Checklist Operativo:</b> 1) Levantar `log_correlator.py` ➔ 2) Exportar `GEMINI_API_KEY` ➔ 3) Iniciar `dispatcher.py` ➔ 4) Ejecutar pruebas de inyección SQL con `curl` simulado.<br/>• <b>Defensa:</b> Explicar cómo el análisis AST descarta el 50% de alertas ruidosas y cómo la tabla `<snort2c>` almacena IPs en RAM sin saturar el disco.", body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("ROL 2: FREDDY VÁSQUEZ CORTÉS — ROUTING, SWITCHING & TELEFONÍA VOIP ASTERISK", h2_style))
    story.append(Paragraph("• <b>Responsabilidades:</b> Troncal 802.1Q en pfSense, segmentación de subredes VLAN (Corp 10, DMZ 20, VoIP 30, Mgmt 99), centralita Asterisk 20 LTS en Docker (`pjsip.conf`, `extensions.conf`, `rtp.conf`), script de disparo telefónico AMI (`call_trigger.py`) y enrutamiento Tailscale.<br/>• <b>Checklist Operativo:</b> 1) `docker compose up -d` en `src/asterisk_pbx/` ➔ 2) Validar registros `pjsip show endpoints` ➔ 3) Probar disparo directo a `PJSIP/1001` ➔ 4) Validar subred `192.168.30.0/24` en consola Tailscale.<br/>• <b>Defensa:</b> Justificar por qué una llamada SIP irrumpe con mayor efectividad que un correo y cómo el aislamiento en VLAN 30 protege la PBX de ataques originados en la DMZ.", body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("ROL 3: CRISTÓBAL QUEZADA — SERVICIOS WEB, PROXY INVERSO HAPROXY & DMZ DVWA", h2_style))
    story.append(Paragraph("• <b>Responsabilidades:</b> Configuración de HAProxy 2.8+ en pfSense, Frontend HTTPS VIP (443) con SSL Offloading, Stick-Tables dinámicas en memoria RAM para mitigación de DoS/Fuzzing L7 (`store http_req_rate(10s),http_err_rate(10s)`) y administración del contenedor vulnerable controlado DVWA en VLAN 20 (`192.168.20.50`).<br/>• <b>Checklist Operativo:</b> 1) Levantar contenedor `docker-compose.dvwa.yml` ➔ 2) Validar frontend y backend en HAProxy ➔ 3) Comprobar respuestas `429 Too Many Requests` ante ráfagas de pruebas.<br/>• <b>Defensa:</b> Explicar cómo HAProxy oculta la infraestructura real de backend y normaliza las cabeceras HTTP antes de que el tráfico alcance a Suricata.", body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("ROL 4: KEVIN RETAMALES — HARDENING PERIMETRAL, PFBLOCKERNG & CONTROL DE CALIDAD (QA)", h2_style))
    story.append(Paragraph("• <b>Responsabilidades:</b> Hardening del kernel pfSense CE 2.9.0, política de aislamiento Zero Trust, integración comunitaria MaxMind GeoLite2 Free, configuración de feeds de reputación FireHOL Level 1 y Spamhaus DROP en pfBlockerNG-devel, y ejecución de matrices de control de calidad QA.<br/>• <b>Checklist Operativo:</b> 1) Comprobar tablas perimetrales `pfctl -s Tables | grep pfB_` ➔ 2) Validar log de bloqueos `/var/log/pfblockerng/ip_block.log` ➔ 3) Ejecutar matriz de pruebas QA de extremo a extremo.<br/>• <b>Defensa:</b> Demostrar cómo las reglas flotantes bloquean botnets en la primera capa y justificar el cumplimiento de costo $0 con la cuenta comunitaria de MaxMind.", body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("4. PROTOCOLO DE DEMOSTRACIÓN EN VIVO (PLAYBOOK DE DEFENSA)", h1_style))
    story.append(Paragraph("1. <b>Inyección SQL en DVWA:</b> El atacante lanza `admin' OR '1'='1 --` contra la web expuesta.<br/>2. <b>Bloqueo en Kernel:</b> Se proyecta la consola SSH de pfSense mostrando el drop en Netmap y la entrada en `<snort2c>`.<br/>3. <b>Timbrado Telefónico:</b> El celular del CISO timbra en vivo vía Asterisk PJSIP.<br/>4. <b>Debriefing Gemini Live:</b> Se activa el altavoz y la IA informa los datos forenses respondiendo preguntas en tiempo real.", body_style))

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=draw_background, onLaterPages=draw_background)
    print(f"Master Roles and Knowledge Base PDF generated: {output_filename}")

if __name__ == "__main__":
    out_pdf = "docs/MANUAL_ROLES_Y_BASE_CONOCIMIENTO_KRONOS.pdf"
    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
    build_pdf(out_pdf)
