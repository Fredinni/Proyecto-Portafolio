#!/usr/bin/env python3
"""
KRONOS SENTINEL - SecOps Master PDF Generator for pfSense Configuration
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
            self.drawString(130, 762, "//  pfSense CE 2.7.2 & Netmap IPS Engineering Manual")
            
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

def build_pfsense_pdf_manual(output_filename: str):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    # Modernist Editorial Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=TEXT_HEADING,
        alignment=1,
        letterSpacing=1.2
    )
    
    badge_style = ParagraphStyle(
        'CoverBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=CYAN_ACCENT,
        alignment=1,
        letterSpacing=1.5
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_MUTED,
        alignment=1
    )
    
    h1_style = ParagraphStyle(
        'SecOpsH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13.5,
        leading=17,
        textColor=CYAN_ACCENT,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SecOpsH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14.5,
        textColor=TEXT_HEADING,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    h3_style = ParagraphStyle(
        'SecOpsH3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=CODE_TEXT,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'SecOpsBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=TEXT_LIGHT,
        spaceAfter=5
    )
    
    code_style = ParagraphStyle(
        'SecOpsCode',
        parent=styles['Code'],
        fontName='Courier-Bold',
        fontSize=7.2,
        leading=10,
        textColor=CODE_TEXT,
        backColor=CODE_BG,
        borderPadding=5,
        spaceBefore=3,
        spaceAfter=5
    )
    
    callout_style = ParagraphStyle(
        'SecOpsCallout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#CBD5E1"),
        backColor=colors.HexColor("#111827"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # =========================================================================
    # PÁGINA 1: PORTADA CORPORATIVA / MINIMALISTA SUIZO
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("SECURITY OPERATIONS &amp; THREAT INTELLIGENCE SPECIFICATION", badge_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("KRONOS <font color='#00E5FF'>SENTINEL</font>", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("MANUAL MAESTRO DE CONFIGURACIÓN Y HARDENING PERIMETRAL<br/>FIREWALL pfSense CE 2.7.2 &amp; SUB-SISTEMA pfctl / SURICATA IPS", subtitle_style))
    story.append(Spacer(1, 14))
    
    # Shield Logo
    logo_path = "assets/sentinel_shield_logo.png"
    if os.path.exists(logo_path):
        img = Image(logo_path, width=105, height=105)
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 14))

    # Meta Box Table (Modernist Minimal Grid)
    meta_data = [
        [Paragraph("<b>PROYECTO:</b>", body_style), Paragraph("KRONOS SENTINEL (APT122 - Portafolio de Título)", body_style)],
        [Paragraph("<b>AUTOR:</b>", body_style), Paragraph("Bruno Urrea Ortiz (Futuro Ing. en Conectividad y Redes)", body_style)],
        [Paragraph("<b>INSTITUCIÓN:</b>", body_style), Paragraph("Duoc UC — Sede San Joaquín", body_style)],
        [Paragraph("<b>SISTEMA BASE:</b>", body_style), Paragraph("FreeBSD 14.0-CURRENT / pfSense CE 2.7.2 (amd64)", body_style)],
        [Paragraph("<b>ARQUITECTURA:</b>", body_style), Paragraph("Inline Netmap IPS + HAProxy SSL + pfBlockerNG + Gemini Live Flash 3.1", body_style)],
        [Paragraph("<b>ESTADO:</b>", body_style), Paragraph("<font color='#10B981'><b>ENTERPRISE VERIFIED &amp; FIELD PRODUCTION READY</b></font>", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[130, 402])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0D131F")),
        ('TEXTCOLOR', (0,0), (-1,-1), TEXT_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#2563EB")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_meta)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: PARTE 1 - WebGUI (MÓDULOS 1, 2 Y 3)
    # =========================================================================
    story.append(Paragraph("PARTE 1: CONFIGURACIÓN POR INTERFAZ GRÁFICA (WebGUI)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=8))

    # MÓDULO 1
    story.append(Paragraph("MÓDULO 1: SETUP BASE, ASIGNACIÓN DE INTERFACES Y VLANs (802.1Q)", h2_style))
    story.append(Paragraph("La arquitectura de red de KRONOS SENTINEL se estructura mediante troncales 802.1Q sobre el adaptador <code>vtnet1</code> (o <code>em1</code>), aislando rigurosamente las zonas corporativas, servidores DMZ y telefonía VoIP:", body_style))

    vlan_table_data = [
        [Paragraph("<b>VLAN Tag</b>", body_style), Paragraph("<b>Interfaz</b>", body_style), Paragraph("<b>Subred IPv4</b>", body_style), Paragraph("<b>Gateway pfSense</b>", body_style), Paragraph("<b>Propósito Táctico</b>", body_style)],
        [Paragraph("<b>VLAN 10</b>", body_style), Paragraph("<code>vtnet1.10</code>", body_style), Paragraph("192.168.10.0/24", body_style), Paragraph("192.168.10.1", body_style), Paragraph("Estaciones de trabajo SOC y clientes.", body_style)],
        [Paragraph("<b>VLAN 20</b>", body_style), Paragraph("<code>vtnet1.20</code>", body_style), Paragraph("192.168.20.0/24", body_style), Paragraph("192.168.20.1", body_style), Paragraph("DMZ (Servidor Web DVWA expuesto).", body_style)],
        [Paragraph("<b>VLAN 30</b>", body_style), Paragraph("<code>vtnet1.30</code>", body_style), Paragraph("192.168.30.0/24", body_style), Paragraph("192.168.30.1", body_style), Paragraph("VoIP Asterisk PBX y Agente de Voz IA.", body_style)],
        [Paragraph("<b>VLAN 99</b>", body_style), Paragraph("<code>vtnet1.99</code>", body_style), Paragraph("192.168.99.0/24", body_style), Paragraph("192.168.99.1", body_style), Paragraph("Gestión Out-of-Band (SSH / WebGUI).", body_style)]
    ]
    t_vlan = Table(vlan_table_data, colWidths=[65, 80, 95, 95, 197])
    t_vlan.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#0D1527"), colors.HexColor("#090D1A")]),
        ('TEXTCOLOR', (0,0), (-1,0), CYAN_ACCENT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, CYAN_ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_vlan)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Procedimiento WebGUI:</b> En <b>Interfaces > Assignments > VLANs</b> registrar tags 10, 20, 30 y 99. Mapear a puertos lógicos (OPT1-OPT4). Configurar servidor DHCP en VLAN 10 (192.168.10.100-200) y reservas estáticas para DVWA (192.168.20.50) y Asterisk PBX (192.168.30.50).", body_style))

    # MÓDULO 2
    story.append(Spacer(1, 4))
    story.append(Paragraph("MÓDULO 2: DESPLIEGUE DE SURICATA EN MODO INLINE IPS (NETMAP ENGINE)", h2_style))
    story.append(Paragraph("Suricata 7.x opera en modo <b>Inline IPS</b> mediante el driver <code>netmap(4)</code> en FreeBSD, descartando paquetes maliciosos en el ring buffer de la tarjeta de red antes de que alcancen el stack IP del kernel:", body_style))
    story.append(Paragraph("• <b>IPS Mode:</b> <code>Inline IPS Mode</code> (Sub-sistema Netmap activo). | <b>Block Offenders:</b> <code>Both</code> (Bidireccional).<br/>"
                           "• <b>Kill States:</b> <code>Enabled</code> (Purga inmediata de estados TCP/UDP activos).<br/>"
                           "• <b>EVE JSON Output:</b> Habilitar salida a <code>/var/log/suricata/eve.json</code> (<i>ALERTS, HTTP, TLS, DROP</i>).<br/>"
                           "• <b>SID Mgmt:</b> Activar <code>dropsid.conf</code> para forzar acción DROP en reglas SQLi (<i>emerging-sqli.rules</i>).", body_style))
    story.append(Paragraph("<b>Advertencia de Hardening:</b> En <b>System > Advanced > Networking</b> desmarcar <i>Hardware Checksum Offloading</i>, <i>TSO</i> y <i>LRO</i>. Netmap requiere calcular checksums directamente para evitar caídas de interfaz.", callout_style))

    # MÓDULO 3
    story.append(Spacer(1, 4))
    story.append(Paragraph("MÓDULO 3: INTELIGENCIA GeoIP MaxMind & THREAT FEEDS (pfBlockerNG-devel)", h2_style))
    story.append(Paragraph("pfBlockerNG-devel filtra tráfico hostil conocido en Capa 3/4 mediante reglas flotantes antes de alcanzar Suricata o HAProxy:", body_style))

    threat_table_data = [
        [Paragraph("<b>Feed / Fuente</b>", body_style), Paragraph("<b>Tipo / URL</b>", body_style), Paragraph("<b>Acción</b>", body_style), Paragraph("<b>Frecuencia</b>", body_style)],
        [Paragraph("<b>MaxMind GeoLite2</b>", body_style), Paragraph("Top Spammers / Países de Alto Riesgo", body_style), Paragraph("<code>Deny Inbound</code>", body_style), Paragraph("Semanal", body_style)],
        [Paragraph("<b>FireHOL Level 1</b>", body_style), Paragraph("firehol_level1.netset (C2/Botnets)", body_style), Paragraph("<code>Deny Inbound</code>", body_style), Paragraph("Cada 6 Horas", body_style)],
        [Paragraph("<b>Spamhaus DROP</b>", body_style), Paragraph("drop.txt / edrop.txt (BGP Hijacks)", body_style), Paragraph("<code>Deny Both</code>", body_style), Paragraph("Diaria", body_style)],
        [Paragraph("<b>ET Compromised</b>", body_style), Paragraph("compromised-ips.txt (Web Exploiters)", body_style), Paragraph("<code>Deny Inbound</code>", body_style), Paragraph("Cada 12 Horas", body_style)]
    ]
    t_threat = Table(threat_table_data, colWidths=[115, 212, 105, 100])
    t_threat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#0D1527"), colors.HexColor("#090D1A")]),
        ('TEXTCOLOR', (0,0), (-1,0), CYAN_ACCENT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, CYAN_ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_threat)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: PARTE 1 - WebGUI (MÓDULOS 4 Y 5)
    # =========================================================================
    story.append(Paragraph("MÓDULO 4: PROXY INVERSO HAPROXY & SEGURIDAD DMZ", h2_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=8))
    story.append(Paragraph("HAProxy ejecuta terminación SSL/TLS y rate-limiting avanzado contra escáneres y ataques de denegación de servicio:", body_style))
    story.append(Paragraph("<b>1. Backend (bk_dvwa_dmz):</b> Servidor <code>192.168.20.50:80</code> con health check activo HTTP y <code>option forwardfor</code>.<br/>"
                           "<b>2. Frontend (fe_wan_https):</b> Binds en puerto 80 (redirige 301 a HTTPS) y puerto 443 con certificado SSL.<br/>"
                           "<b>3. Stick Tables en Memoria:</b><br/>"
                           "• Control de conexiones TCP: rechazo si <code>conn_cur > 20</code> o <code>conn_rate(3s) > 30</code>.<br/>"
                           "• Control de peticiones HTTP: respuesta 429 si <code>http_req_rate(10s) > 80</code>.<br/>"
                           "• Detección de Fuzzers: bloqueo si errores 4xx <code>http_err_rate(10s) > 25</code>.<br/>"
                           "• Sanitización de Cabeceras: inyección de <code>X-Forwarded-For</code> y <code>X-Real-IP</code> para evitar IP spoofing.", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("MÓDULO 5: MATRIZ DE REGLAS ZERO TRUST (WAN, DMZ, VOIP)", h2_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=8))
    
    rules_table_data = [
        [Paragraph("<b>Interfaz</b>", body_style), Paragraph("<b>Acción</b>", body_style), Paragraph("<b>Origen</b>", body_style), Paragraph("<b>Destino</b>", body_style), Paragraph("<b>Puerto / Protocolo</b>", body_style), Paragraph("<b>Descripción</b>", body_style)],
        [Paragraph("WAN", body_style), Paragraph("<code>PASS</code>", body_style), Paragraph("Cualquiera", body_style), Paragraph("WAN Address", body_style), Paragraph("80, 443 (TCP)", body_style), Paragraph("Ingreso Web a HAProxy.", body_style)],
        [Paragraph("DMZ", body_style), Paragraph("<code>BLOCK</code>", body_style), Paragraph("DMZ net", body_style), Paragraph("LAN net / MGMT", body_style), Paragraph("Cualquiera", body_style), Paragraph("Aislamiento total de LAN.", body_style)],
        [Paragraph("DMZ", body_style), Paragraph("<code>BLOCK</code>", body_style), Paragraph("DMZ net", body_style), Paragraph("pfSense IP", body_style), Paragraph("80, 443, 22 (TCP)", body_style), Paragraph("Hardening Firewall GUI.", body_style)],
        [Paragraph("VoIP", body_style), Paragraph("<code>PASS</code>", body_style), Paragraph("VoIP net", body_style), Paragraph("192.168.30.50", body_style), Paragraph("5060 (UDP/TCP)", body_style), Paragraph("Señalización SIP PJSIP.", body_style)],
        [Paragraph("VoIP", body_style), Paragraph("<code>PASS</code>", body_style), Paragraph("VoIP net", body_style), Paragraph("192.168.30.50", body_style), Paragraph("10000:10100 (UDP)", body_style), Paragraph("Canales de audio RTP.", body_style)]
    ]
    t_rules = Table(rules_table_data, colWidths=[50, 52, 85, 95, 95, 155])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#0D1527"), colors.HexColor("#090D1A")]),
        ('TEXTCOLOR', (0,0), (-1,0), CYAN_ACCENT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, CYAN_ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_rules)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 4: PARTE 2 - GUÍA AVANZADA CLI / SHELL DE FREEBSD
    # =========================================================================
    story.append(Paragraph("PARTE 2: CONFIGURACIÓN AVANZADA MEDIANTE CLI / SHELL DE FREEBSD", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=8))

    story.append(Paragraph("2.1 Manipulación de la Tabla de Kernel <code>snort2c</code> con <code>pfctl</code>", h3_style))
    story.append(Paragraph("El sub-sistema <code>pfctl</code> interactúa a nivel atómico con el kernel de FreeBSD:", body_style))
    
    code_pfctl = (
        "# 1. Listar todas las direcciones IP bloqueadas en la tabla snort2c:\n"
        "pfctl -t snort2c -T show\n\n"
        "# 2. Test atómico en kernel (Retorna 0 si existe, 1 si no existe):\n"
        "pfctl -t snort2c -T test 185.220.101.5\n\n"
        "# 3. Insertar dinámicamente una IP atacante:\n"
        "pfctl -t snort2c -T add 185.220.101.5\n\n"
        "# 4. Purgar estados de conexión activos bidireccionalmente (Kill States):\n"
        "pfctl -k 185.220.101.5\n"
        "pfctl -k 0.0.0.0/0 -k 185.220.101.5\n\n"
        "# 5. Estadísticas de paquetes descartados en memoria por tabla:\n"
        "pfctl -vvsTables | grep -A 8 snort2c"
    )
    story.append(Preformatted(code_pfctl, code_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("2.2 Sintonización de Alto Rendimiento para Netmap y Tablas pf", h3_style))
    code_sysctl = (
        "# Aumentar límite máximo de entradas en tablas pf a 4 Millones:\n"
        "sysctl net.pf.request_maxcount=4000000\n\n"
        "# Optimizar ring buffers del subsystem netmap(4):\n"
        "sysctl dev.netmap.ring_size=4096\n"
        "sysctl dev.netmap.buf_size=2048"
    )
    story.append(Preformatted(code_sysctl, code_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("2.3 Servicio Init Autónomo en FreeBSD (<code>/usr/local/etc/rc.d/kronos_sentinel.sh</code>)", h3_style))
    code_rc = (
        "#!/bin/sh\n"
        "# PROVIDE: kronos_sentinel\n"
        "# REQUIRE: NETWORKING suricata\n"
        ". /etc/rc.subr\n"
        "name=\"kronos_sentinel\"\n"
        "rcvar=\"kronos_sentinel_enable\"\n"
        "command=\"/usr/local/bin/python3\"\n"
        "command_args=\"/usr/local/share/kronos/log_correlator.py > /var/log/kronos.log 2>&1 &\"\n"
        "load_rc_config $name\n"
        ": ${kronos_sentinel_enable:=\"YES\"}\n"
        "run_rc_command \"$1\""
    )
    story.append(Preformatted(code_rc, code_style))

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=draw_background, onLaterPages=draw_background)
    print(f"Master PDF generated successfully: {output_filename}")

if __name__ == "__main__":
    output_pdf = "docs/Manual_Configuracion_pfSense_KRONOS_SENTINEL.pdf"
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    build_pfsense_pdf_manual(output_pdf)
