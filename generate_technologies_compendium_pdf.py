#!/usr/bin/env python3
"""
KRONOS SENTINEL - Technologies & Architecture Compendium PDF Generator ($0 Cost Policy)
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
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
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(CYAN_ACCENT)
            self.drawString(40, 762, "KRONOS SENTINEL")
            
            self.setFont("Helvetica", 7.5)
            self.setFillColor(TEXT_MUTED)
            self.drawString(130, 762, "//  Technologies, Protocols & Architecture Compendium")
            
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(TEXT_LIGHT)
            self.drawRightString(572, 762, "DUOC UC SAN JOAQUÍN")
            
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(40, 754, 572, 754)
            
        # Footer
        self.setFont("Helvetica", 7.5)
        self.setFillColor(TEXT_MUTED)
        self.drawString(40, 28, "KRONOS SENTINEL (APT122) • AUTOR: BRUNO URREA ORTIZ")
        
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(CYAN_ACCENT)
        self.drawRightString(572, 28, f"PÁGINA {self._pageNumber} / {page_count}")
        
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(40, 38, 572, 38)
        
        self.restoreState()

def draw_background(canvas_obj, doc):
    """Draws full-page matte slate background."""
    canvas_obj.saveState()
    canvas_obj.setFillColor(BG_COLOR)
    canvas_obj.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=True, stroke=False)
    canvas_obj.restoreState()

def build_technologies_pdf(output_filename: str):
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
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=TEXT_HEADING,
        alignment=1,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=CYAN_ACCENT,
        alignment=1,
        spaceAfter=4
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=TEXT_MUTED,
        alignment=1,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=14.5,
        textColor=CYAN_ACCENT,
        spaceBefore=7,
        spaceAfter=4
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=TEXT_HEADING,
        spaceBefore=5,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=TEXT_LIGHT,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=CRIMSON_BADGE,
        spaceBefore=3,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7,
        leading=9,
        textColor=CODE_TEXT,
        backColor=CODE_BG,
        borderColor=BORDER_COLOR,
        borderWidth=0.5,
        borderPadding=4,
        spaceBefore=2,
        spaceAfter=3
    )

    story = []

    # =========================================================================
    # PÁGINA 1: PORTADA & CAPAS 1 Y 2 (FIREWALL, NETMAP IPS Y FIRMAS)
    # =========================================================================
    logo_path = "assets/sentinel_shield_logo.png"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=85, height=85))
        story.append(Spacer(1, 4))

    story.append(Paragraph("COMPENDIO TÉCNICO DE TECNOLOGÍAS, PROTOCOLOS Y ARQUITECTURA", title_style))
    story.append(Paragraph("DESGLOSE DE FUNCIONAMIENTO INTERNO &amp; LICENCIAMIENTO // KRONOS SENTINEL", subtitle_style))
    story.append(Paragraph("<b>Autor:</b> Bruno Urrea Ortiz | Escuela de Informática y Telecomunicaciones — Duoc UC Sede San Joaquín<br/><b>Estado:</b> Prototipo Funcional en Desarrollo y Validación de Laboratorio • <b>Costo:</b> $0 CLP", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=6))

    story.append(Paragraph("1. CAPA PERIMETRAL &amp; KERNEL DE FREEBSD", h1_style))
    story.append(Paragraph("<b>1.1 pfSense CE 2.9.0 &amp; Packet Filter (pf):</b><br/>"
                           "pfSense CE es la distribución de seguridad perimetral basada en FreeBSD 14. El subsistema <code>pf(4)</code> gestiona la inspección de estados en memoria (SPI). Utiliza <b>Tablas pf</b> (estructuras <code>struct pfr_ktable</code> en C) indexadas mediante árboles binarios Radix con tiempo de búsqueda atómico $O(1)$. Administra la tabla <code>&lt;snort2c&gt;</code> para el bloqueo instantáneo en memoria sin costo computacional. <i>(100% Open Source FreeBSD, $0 CLP)</i>.", body_style))

    story.append(Paragraph("<b>1.2 Suricata 7.x en Modo Inline IPS (Netmap Engine):</b><br/>"
                           "Suricata es el motor de inspección profunda de paquetes (DPI) multi-hilo. En modo <b>Inline IPS</b> opera sobre el framework <code>netmap(4)</code> de FreeBSD, desacoplando los ring buffers de la tarjeta de red del stack TCP/IP del kernel. Los paquetes se analizan en memoria compartida zero-copy. Si coinciden con una regla DROP, se descartan físicamente en el descriptor de hardware en microsegundos, serializando la telemetría en <code>/var/log/suricata/eve.json</code>. <i>(GPLv2, $0 CLP)</i>.", body_style))

    story.append(Paragraph("<b>1.3 Reglas ET Open (Emerging Threats) &amp; Snort Community:</b><br/>"
                           "Firmas comunitarias abiertas de capa 7 basadas en expresiones regulares PCRE que identifican patrones maliciosos en tráfico HTTP/SQLi (ej. <code>UNION SELECT</code>, <code>OR 1=1</code>). Mediante <code>dropsid.conf</code>, KRONOS transforma alertas en acciones de drop atómico. <i>(Comunitario Abierto, $0 CLP)</i>.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: CAPAS 3 Y 4 (pfBlockerNG, HAPROXY, DVWA Y MOTOR PFCTL)
    # =========================================================================
    story.append(Paragraph("2. CAPA DE SEGURIDAD WEB, DMZ &amp; MOTOR DE CORRELACIÓN", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=6))

    story.append(Paragraph("<b>2.1 pfBlockerNG-devel &amp; MaxMind GeoLite2 Free:</b><br/>"
                           "Gestiona inteligencia geográfica y reputación IP. Descarga la base binaria <code>GeoLite2-Country.mmdb</code> y compila rangos CIDR de países <i>Top Spammers</i> y listas C2 (FireHOL L1, Spamhaus DROP). Inyecta reglas flotantes de alta prioridad que descartan el 40% del tráfico ruidoso antes de alcanzar Suricata o HAProxy. <i>(GPLv3 / MaxMind Free, $0 CLP)</i>.", body_style))

    story.append(Paragraph("<b>2.2 HAProxy 2.8+ Community Edition &amp; Stick Tables:</b><br/>"
                           "Proxy inverso y balanceador de alta disponibilidad. Realiza terminación SSL/TLS (puerto 443) e inyecta encabezados <code>X-Forwarded-For</code>. Utiliza <b>Stick Tables</b> en memoria RAM (<code>table type ip size 100k expire 30s store http_req_rate(10s)</code>) para mitigar escaneos agresivos, denegación de servicio L7 y responder 429 Too Many Requests ante fuzzing. <i>(GPLv2/LGPLv2.1, $0 CLP)</i>.", body_style))

    story.append(Paragraph("<b>2.3 DVWA (Damn Vulnerable Web Application) en Docker:</b><br/>"
                           "Aplicación web PHP/MySQL intencionalmente vulnerable aislada en la VLAN 20 DMZ (<code>192.168.20.50</code>). Sirve como entorno objetivo controlado para validar ataques reales con <code>sqlmap</code> o scripts de explotación. <i>(GPLv3, $0 CLP)</i>.", body_style))

    story.append(Paragraph("<b>2.4 Motor Heurístico KRONOS (Python 3.12 + FreeBSD pfctl):</b><br/>"
                           "Núcleo analítico de KRONOS. Monitorea <code>eve.json</code> en tiempo real, aplica un filtro de supresión de falsos positivos (>50% de ruido genérico descartado), evalúa operadores relacionales SQLi mediante análisis AST y verifica el bloqueo en kernel con <code>pfctl -t snort2c -T test &lt;IP&gt;</code> antes de disparar el webhook de llamada. <i>(Licencia MIT, Código Propio, $0 CLP)</i>.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: TELEFONÍA VOIP, IA GEMINI LIVE Y TAILSCALE ZERO TRUST
    # =========================================================================
    story.append(Paragraph("3. CAPA DE TELEFONÍA VOIP, IA MULTIMODAL &amp; ZERO TRUST", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=6))

    story.append(Paragraph("<b>3.1 Asterisk 20 LTS PBX en Contenedor Docker:</b><br/>"
                           "Centralita telefónica SIP/PJSIP. Administra anexos de usuarios (1001 Bruno, 1002 Freddy, 1003 Cristóbal, 1004 Kevin) y el anexo del agente IA (1000). Expone el socket TCP administrativo <b>AMI (puerto 5038)</b> para ejecutar <code>Action: Originate</code> al dispararse una alarma y canalizar el audio RTP bidireccional (puertos UDP 10000:10100). <i>(GPLv2, $0 CLP)</i>.", body_style))

    story.append(Paragraph("<b>3.2 Google Gemini Live API Flash 3.1 (Audio Multimodal en Tiempo Real):</b><br/>"
                           "Modelo de Inteligencia Artificial generativa multimodal de ultrabaja latencia de Google DeepMind. Se conecta mediante <b>WebSocket WSS sobre HTTPS (puerto 443)</b> con <code>generativelanguage.googleapis.com</code>. Procesa y genera audio nativo en tiempo real (PCM 24kHz) sin latencias de transcripción separada. Asume el rol de analista SecOps, informando la IP atacante, país GeoIP, payload del vector y asesorando al CISO en medidas de mitigación. <i>(Google AI Studio Free Tier, $0 CLP)</i>.", body_style))

    story.append(Paragraph("<b>3.3 Tailscale Zero Trust WireGuard Mesh (Subnet Router):</b><br/>"
                           "Red privada mallada basada en el protocolo criptográfico WireGuard (Curve25519, ChaCha20). pfSense anuncia la subred VoIP <code>192.168.30.0/24</code> como <b>Subnet Router</b>. El smartphone del CISO se conecta a la Tailnet privada y registra su softphone (Zoiper) directamente a Asterisk sin abrir puertos SIP a Internet ni sufrir bloqueos por CGNAT. <i>(Tailscale Free Community, $0 CLP)</i>.", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("4. MATRIZ DE LICENCIAMIENTO &amp; COSTO TOTAL DE LA ARQUITECTURA", h1_style))
    
    mat_table_data = [
        [Paragraph("<b>Tecnología</b>", body_style), Paragraph("<b>Rol en KRONOS</b>", body_style), Paragraph("<b>Licencia / Modelo</b>", body_style), Paragraph("<b>Costo</b>", body_style)],
        [Paragraph("<b>pfSense CE 2.9.0</b>", body_style), Paragraph("Firewall L2-L4, VLANs y tabla snort2c", body_style), Paragraph("FreeBSD Open Source", body_style), Paragraph("<b>$0 CLP</b>", body_style)],
        [Paragraph("<b>Suricata 7.x</b>", body_style), Paragraph("Inline Netmap IPS y Drop atómico", body_style), Paragraph("GPLv2 Open Source", body_style), Paragraph("<b>$0 CLP</b>", body_style)],
        [Paragraph("<b>Reglas ET Open</b>", body_style), Paragraph("Firmas L7 SQLi y Exploits", body_style), Paragraph("Community Free Rules", body_style), Paragraph("<b>$0 CLP</b>", body_style)],
        [Paragraph("<b>pfBlockerNG</b>", body_style), Paragraph("GeoIP MaxMind y Threat Feeds", body_style), Paragraph("GPLv3 / GeoLite2 Free", body_style), Paragraph("<b>$0 CLP</b>", body_style)],
        [Paragraph("<b>HAProxy 2.8+</b>", body_style), Paragraph("Terminación SSL y Stick-Tables anti-DoS", body_style), Paragraph("GPLv2 / LGPLv2.1", body_style), Paragraph("<b>$0 CLP</b>", body_style)],
        [Paragraph("<b>DVWA Docker</b>", body_style), Paragraph("Entorno web vulnerable en DMZ", body_style), Paragraph("GPLv3 Open Source", body_style), Paragraph("<b>$0 CLP</b>", body_style)],
        [Paragraph("<b>Motor pfctl</b>", body_style), Paragraph("Supresión de falsos positivos (>50%)", body_style), Paragraph("MIT (Código Propio)", body_style), Paragraph("<b>$0 CLP</b>", body_style)],
        [Paragraph("<b>Asterisk 20 PBX</b>", body_style), Paragraph("Telefonía SIP PJSIP y Auto-Dialer", body_style), Paragraph("GPLv2 Open Source", body_style), Paragraph("<b>$0 CLP</b>", body_style)],
        [Paragraph("<b>Gemini Live 3.1</b>", body_style), Paragraph("Voz IA bidireccional debriefing CISO", body_style), Paragraph("Google AI Studio Free Tier", body_style), Paragraph("<b>$0 CLP</b>", body_style)],
        [Paragraph("<b>Tailscale Mesh</b>", body_style), Paragraph("Subnet Router Zero Trust para Softphone", body_style), Paragraph("WireGuard Free Plan", body_style), Paragraph("<b>$0 CLP</b>", body_style)]
    ]
    t_mat = Table(mat_table_data, colWidths=[95, 172, 115, 60])
    t_mat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#0D1527"), colors.HexColor("#090D1A")]),
        ('TEXTCOLOR', (0,0), (-1,0), CYAN_ACCENT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, CYAN_ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_mat)

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=draw_background, onLaterPages=draw_background)
    print(f"Technologies Compendium PDF generated successfully: {output_filename}")

if __name__ == "__main__":
    output_pdf = "docs/COMPENDIO_TECNOLOGIAS_Y_ARQUITECTURA_KRONOS.pdf"
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    build_technologies_pdf(output_pdf)
