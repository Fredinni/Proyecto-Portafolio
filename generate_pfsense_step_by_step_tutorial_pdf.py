#!/usr/bin/env python3
"""
KRONOS SENTINEL - Master Multi-Phase Step-by-Step pfSense CE 2.9.0 Tutorial Generator
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
Features: High-Fidelity WebGUI Simulated Mockup Cards, Official Netgate Parameters, 8-Page Guide
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

# GUI Mockup Palette (Bootstrap Dark pfSense style)
GUI_HEADER_BG = colors.HexColor("#111827")
GUI_BODY_BG = colors.HexColor("#0B1120")
GUI_INNER_BORDER = colors.HexColor("#1E293B")

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
            self.drawString(130, 762, "//  pfSense CE 2.9.0 Master Step-by-Step WebGUI Guide")
            
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

def make_gui_mockup(title_path: str, fields: list, styles):
    """Generates a realistic pfSense WebGUI UI simulated card table."""
    body_style = styles['BodyDark']
    
    rows = []
    # Header bar with pfSense icon and breadcrumb
    header_html = (
        f"<table width='100%'><tr>"
        f"<td><b><font color='#00E5FF'>🌐 pfSense WebGUI</font></b> <font color='#64748B'>// </font><font color='#F8FAFC'><b>{title_path}</b></font></td>"
        f"<td align='right'><font color='#94A3B8'>v2.9.0-RELEASE (amd64)</font></td>"
        f"</tr></table>"
    )
    rows.append([Paragraph(header_html, body_style), ""])
    
    for label, val in fields:
        p_label = Paragraph(f"<b><font color='#94A3B8'>{label}</font></b>", body_style)
        if isinstance(val, str) and val.startswith("btn:"):
            btn_text = val.replace("btn:", "")
            p_val = Paragraph(f"<b><font color='#38BDF8'>{btn_text}</font></b>", body_style)
        elif isinstance(val, str) and val.startswith("note:"):
            note_text = val.replace("note:", "")
            p_val = Paragraph(f"<font color='#F59E0B'><i>{note_text}</i></font>", body_style)
        else:
            p_val = Paragraph(f"<font color='#38BDF8'><code>{val}</code></font>", body_style)
        rows.append([p_label, p_val])
        
    t = Table(rows, colWidths=[165, 367])
    t_style = [
        ('SPAN', (0,0), (1,0)),
        ('BACKGROUND', (0,0), (-1,0), GUI_HEADER_BG),
        ('BACKGROUND', (0,1), (-1,-1), GUI_BODY_BG),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#2563EB")),
        ('INNERGRID', (0,1), (-1,-1), 0.5, GUI_INNER_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]
    t.setStyle(TableStyle(t_style))
    return t

def build_master_tutorial_pdf(output_filename: str):
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
        fontSize=17,
        leading=21,
        textColor=TEXT_HEADING,
        alignment=1,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=CYAN_ACCENT,
        alignment=1,
        spaceAfter=3
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=TEXT_MUTED,
        alignment=1,
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13.5,
        textColor=CYAN_ACCENT,
        spaceBefore=5,
        spaceAfter=2
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11.5,
        textColor=TEXT_HEADING,
        spaceBefore=4,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=TEXT_LIGHT,
        spaceAfter=2
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9.5,
        textColor=CRIMSON_BADGE,
        spaceBefore=2,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.5,
        leading=8.5,
        textColor=CODE_TEXT,
        backColor=CODE_BG,
        borderColor=BORDER_COLOR,
        borderWidth=0.5,
        borderPadding=3,
        spaceBefore=2,
        spaceAfter=3
    )

    styles.add(body_style)
    styles.add(code_style)

    story = []

    # =========================================================================
    # PÁGINA 1: PORTADA & FASE 1 (SETUP INICIAL & HARDWARE TUNING)
    # =========================================================================
    logo_path = "assets/sentinel_shield_logo.png"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=75, height=75))
        story.append(Spacer(1, 3))

    story.append(Paragraph("MANUAL MAESTRO DE CONFIGURACIÓN PASO A PASO: pfSense CE 2.9.0", title_style))
    story.append(Paragraph("BLUEPRINT VISUAL, SIMULACIÓN WebGUI Y PARÁMETROS OFICIALES DE LABORATORIO", subtitle_style))
    story.append(Paragraph("<b>Autor:</b> Bruno Urrea Ortiz | Duoc UC Sede San Joaquín • <b>Portafolio de Título APT122</b> ($0 CLP)", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=5))

    story.append(Paragraph("FASE 1: SETUP INICIAL, HARDWARE TUNING &amp; NETWORKING BASE", h1_style))
    
    story.append(Paragraph("PASO 1.1: CONFIGURACIÓN GENERAL DEL SISTEMA Y SERVIDORES DNS", h2_style))
    gui_p1_1 = make_gui_mockup(
        "System / General Setup",
        [
            ("Hostname & Domain", "kronos-fw . kronos.local"),
            ("DNS Server Settings", "DNS 1: 1.1.1.1 (Gateway: none) | DNS 2: 8.8.8.8"),
            ("DNS Server Override", "[ ] Allow DNS server list to be overridden by DHCP on WAN"),
            ("DNS Resolution Behavior", "Use local DNS (127.0.0.1), fall back to remote DNS Servers [▼]"),
            ("Timezone & NTP", "America/Santiago (Chile Standard Time) | 0.south-america.pool.ntp.org"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p1_1)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 1.2: HARDWARE OFFLOADING TUNING (MANDATORIO PARA NETMAP INLINE IPS)", h2_style))
    gui_p1_2 = make_gui_mockup(
        "System / Advanced / Networking ➔ Network Interfaces",
        [
            ("Hardware Checksum Offload", "[X] Disable hardware checksum offload (Desactiva cálculo por NIC)"),
            ("Hardware TCP Segmentation", "[X] Disable hardware TCP segmentation offload (TSO) (Mandatorio para Netmap)"),
            ("Hardware Large Receive", "[X] Disable hardware large receive offload (LRO) (Evita agregación previa a IPS)"),
            ("Netgate Doc Note", "note:CRÍTICO: El framework netmap(4) en modo Inline IPS colisiona si el hardware offloading está activo."),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ] (Requiere reiniciar el sistema)")
        ],
        styles
    )
    story.append(gui_p1_2)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: PASO 1.3 (VLANs) & PASO 1.4 (ASIGNACIÓN DE INTERFACES E IP)
    # =========================================================================
    story.append(Paragraph("PASO 1.3: CONFIGURACIÓN DE TRONCAL 802.1Q Y CREACIÓN DE VLANs", h1_style))
    story.append(Paragraph("Navegar a <code>Interfaces > Assignments > VLANs</code> y registrar los 4 tags de subred sobre el adaptador físico:", body_style))
    
    gui_p1_3 = make_gui_mockup(
        "Interfaces / VLANs / Edit",
        [
            ("Parent Interface", "vtnet1 (LAN Trunk Physical Adapter) [▼]"),
            ("VLAN Tag 10 (Corporativa)", "Tag: 10 | Priority: 0 | Description: VLAN_10_CORP_INTERNAL"),
            ("VLAN Tag 20 (DMZ Web)", "Tag: 20 | Priority: 0 | Description: VLAN_20_DMZ_SERVERS"),
            ("VLAN Tag 30 (VoIP PBX)", "Tag: 30 | Priority: 0 | Description: VLAN_30_VOIP_PBX"),
            ("VLAN Tag 99 (Gestión SecOps)", "Tag: 99 | Priority: 0 | Description: VLAN_99_MGMT_SEC"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p1_3)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 1.4: ASIGNACIÓN DE INTERFACES Y DIRECCIONAMIENTO IP ESTÁTICO", h1_style))
    story.append(Paragraph("Navegar a <code>Interfaces > Assignments</code> para enlazar cada VLAN y configurar su puerta de enlace:", body_style))
    
    gui_p1_4 = make_gui_mockup(
        "Interfaces / DMZ_SERVERS (vtnet1.20) & WAN (vtnet0)",
        [
            ("Enable Interface", "[X] Enable interface"),
            ("IPv4 Configuration Type", "Static IPv4 [▼]"),
            ("IPv4 Address (DMZ_SERVERS)", "192.168.20.1 / 24 | IPv4 Upstream Gateway: None [▼]"),
            ("IPv4 Address (LAN_CORP)", "192.168.10.1 / 24 | IPv4 Address (VOIP_PBX): 192.168.30.1 / 24"),
            ("IPv4 Address (MGMT_SEC)", "192.168.99.1 / 24 | IPv4 Address (WAN): 198.51.100.1 / 24 (Lab Dual-Host)"),
            ("WAN RFC 1918 / Bogon Filter", "[ ] Block private networks   [ ] Block bogon networks (Desmarcados en Lab)"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p1_4)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: FASE 2 (SERVICIOS DHCP Y RESERVAS ESTÁTICAS DVWA & ASTERISK)
    # =========================================================================
    story.append(Paragraph("FASE 2: SERVICIOS DHCP Y RESERVAS ESTÁTICAS DE INFRAESTRUCTURA", h1_style))
    
    story.append(Paragraph("PASO 2.1: SERVIDOR DHCP Y RESERVA FIJA PARA EL SERVIDOR WEB DMZ (DVWA)", h2_style))
    gui_p2_1 = make_gui_mockup(
        "Services / DHCP Server / DMZ_SERVERS (VLAN 20)",
        [
            ("Enable DHCP Server", "[X] Enable DHCP server on DMZ_SERVERS interface"),
            ("Subnet & Subnet Mask", "192.168.20.0 / 255.255.255.0 (Available Range: .1 to .254)"),
            ("Dynamic Pool Range", "From: 192.168.20.100  To: 192.168.20.199"),
            ("DNS & Default Gateway", "DNS: 192.168.20.1, 1.1.1.1 | Gateway: 192.168.20.1"),
            ("Static Mapping DVWA Target", "MAC: 02:42:c0:a8:14:32 ➔ IP Fija: 192.168.20.50 (dvwa-dmz-target)"),
            ("Static Lease Description", "Laboratorio Web Vulnerable Controlado - DMZ"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p2_1)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 2.2: SERVIDOR DHCP Y RESERVA FIJA PARA CENTRALITA ASTERISK PBX", h2_style))
    gui_p2_2 = make_gui_mockup(
        "Services / DHCP Server / VOIP_PBX (VLAN 30)",
        [
            ("Enable DHCP Server", "[X] Enable DHCP server on VOIP_PBX interface"),
            ("Dynamic Pool Range", "From: 192.168.30.100  To: 192.168.30.199"),
            ("DNS & Default Gateway", "DNS: 192.168.30.1 | Gateway: 192.168.30.1"),
            ("Static Mapping Asterisk PBX", "MAC: 02:42:c0:a8:1e:32 ➔ IP Fija: 192.168.30.50 (asterisk-pbx-core)"),
            ("Static Lease Description", "Centralita Telefonica SIP/PJSIP y Auto-Dialer SOAR"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p2_2)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 4: FASE 3 (SURICATA 7.X NETMAP INLINE IPS & DROPSID)
    # =========================================================================
    story.append(Paragraph("FASE 3: SURICATA 7.X — PREVENCIÓN EN KERNEL (NETMAP INLINE IPS)", h1_style))
    
    story.append(Paragraph("PASO 3.1: CONFIGURACIÓN GLOBAL DE REGLAS (ET OPEN &amp; SNORT COMMUNITY)", h2_style))
    gui_p3_1 = make_gui_mockup(
        "Services / Suricata / Global Settings",
        [
            ("Install ETOpen Rules", "[X] Install Emerging Threats Open rules (Free Community Edition $0)"),
            ("Install Snort Rules", "[X] Install Snort Community rules (Cisco Talos Open Ruleset $0)"),
            ("Snort Oinkmaster Code", "none (No requerido para Snort Community Free Tier)"),
            ("Update Interval & Live Swap", "Update Interval: 12 Hours [▼] | [X] Live rule swap on update"),
            ("Acciones WebGUI", "btn:[ Save ]")
        ],
        styles
    )
    story.append(gui_p3_1)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 3.2: CONFIGURACIÓN DE LA INTERFAZ WAN EN MODO INLINE IPS (NETMAP)", h2_style))
    gui_p3_2 = make_gui_mockup(
        "Services / Suricata / Interfaces / Edit [WAN Settings]",
        [
            ("Enable & Interface", "[X] Enable inspection | Interface: WAN (vtnet0) [▼]"),
            ("IPS Mode Selection", "( ) Legacy Mode   (X) Inline Mode (netmap framework)"),
            ("Block on Alerts & Kill States", "[X] Block offenders (Hardware ring-buffer drop) | [X] Kill active states"),
            ("EVE JSON Telemetry", "[X] Enable EVE JSON Log | Type: (X) FILE (/var/log/suricata/eve.json)"),
            ("EVE Event Types", "[X] Alerts (SQLi/RCE)   [X] HTTP (URI, Host, Headers)   [X] TLS"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p3_2)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 3.3: GESTIÓN DE FIRMAS ET OPEN Y POLÍTICA dropsid.conf", h2_style))
    gui_p3_3 = make_gui_mockup(
        "Services / Suricata / SID Mgmt / dropsid.conf",
        [
            ("Automatic SID Mgmt", "[X] Enable Automatic SID State Management"),
            ("Drop SID List Selection", "dropsid.conf [▼] (Transforma alertas en Drops atómicos)"),
            ("Categorias PCRE Monitoreadas", "pcre:emerging-sql, pcre:emerging-exploit, pcre:community-web-attacks"),
            ("State Order Evaluation", "Drop > Enable > Disable"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p3_3)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 5: FASE 4 (pfBlockerNG-devel GEOIP & THREAT FEEDS)
    # =========================================================================
    story.append(Paragraph("FASE 4: INTELIGENCIA DE AMENAZAS CON pfBlockerNG-devel Y MAXMIND GEOIP", h1_style))
    
    story.append(Paragraph("PASO 4.1: CONFIGURACIÓN DE MAXMIND GEOIP FREE TIER", h2_style))
    gui_p4_1 = make_gui_mockup(
        "Firewall / pfBlockerNG / IP / GeoIP",
        [
            ("MaxMind Account ID & Key", "Account ID: 1024982 | License Key: ******************** ($0 Free Tier)"),
            ("Top Spammers GeoIP", "CN, RU, IR, KP, VN, NG [▼]"),
            ("List Action", "( ) Disabled   ( ) Permit   (X) Deny Inbound   ( ) Deny Both"),
            ("Logging Configuration", "[X] Enable pfBlockerNG log (/var/log/pfblockerng/ip_block.log)"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p4_1)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 4.2: FEEDS DE REPUTACIÓN IP GLOBALES (FireHOL &amp; Spamhaus DROP)", h2_style))
    gui_p4_2 = make_gui_mockup(
        "Firewall / pfBlockerNG / IP / IP Feeds / Edit",
        [
            ("Feed 1 (FireHOL L1)", "URL: https://iplists.firehol.org/files/firehol_level1.netset | Action: Deny Inbound"),
            ("Feed 2 (Spamhaus DROP)", "URL: https://www.spamhaus.org/drop/drop.txt | Action: Deny Inbound"),
            ("Update Frequency", "Every 4 Hours [▼] | State: ON [▼]"),
            ("Automatic Rule Order", "| pfB_Block (Floating Rules Top Priority) [▼]"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p4_2)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 6: FASE 5 (HAPROXY 2.8+ SSL & STICK-TABLES ANTI-FUZZING)
    # =========================================================================
    story.append(Paragraph("FASE 5: PROXY INVERSO HAPROXY 2.8+ Y PROTECCIÓN ANTI-DOS / FUZZING", h1_style))
    
    story.append(Paragraph("PASO 5.1: CONFIGURACIÓN DEL BACKEND (DVWA EN DMZ)", h2_style))
    gui_p5_1 = make_gui_mockup(
        "Services / HAProxy / Backend / Edit: DVWA_DMZ_POOL",
        [
            ("Backend Name & Mode", "Name: DVWA_DMZ_POOL | Mode: active [▼] | Balance: roundrobin [▼]"),
            ("Server List Target", "dvwa-node ➔ Forward to: Address+Port ➔ IP: 192.168.20.50 | Port: 80"),
            ("Backend Encryption", "[ ] Encrypt connection to backend (HTTP Plano en DMZ interna)"),
            ("Health Check Method", "HTTP [▼] | HTTP check URI: /index.php | Check Frequency: 2000 ms"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p5_1)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 5.2: CONFIGURACIÓN DEL FRONTEND SSL Y STICK-TABLES DE RATE LIMITING", h2_style))
    gui_p5_2 = make_gui_mockup(
        "Services / HAProxy / Frontend / Edit: KRONOS_HTTPS_VIP",
        [
            ("Frontend Name & Address", "Name: KRONOS_HTTPS_FRONTEND | Listen: WAN address (198.51.100.1):443"),
            ("SSL Offloading Cert", "Type: (X) SSL / HTTPS offloading | Cert: KRONOS_LAB_CERT (RSA 2048)"),
            ("Advanced Pass Thru (Stick Tables)", "stick-table type ip size 100k expire 30s store http_req_rate(10s),http_err_rate(10s)"),
            ("Anti-DoS ACL Rule 1", "http-request track-sc0 src | http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }"),
            ("Anti-Fuzzing ACL Rule 2", "http-request deny deny_status 403 if { sc_http_err_rate(0) gt 25 }"),
            ("Default Backend Pool", "DVWA_DMZ_POOL [▼]"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p5_2)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 7: FASE 6 (FIREWALL ZERO TRUST) & FASE 7 (TAILSCALE SUBNET ROUTER)
    # =========================================================================
    story.append(Paragraph("FASE 6: MATRIZ DE REGLAS DE FIREWALL ZERO TRUST", h1_style))
    
    story.append(Paragraph("PASO 6.1: REGLAS DE AISLAMIENTO DMZ Y PERÍMETRO WAN", h2_style))
    gui_p6_1 = make_gui_mockup(
        "Firewall / Rules / DMZ_SERVERS (VLAN 20)",
        [
            ("Regla 1 (DNS/NTP Base)", "PASS IPv4 UDP ➔ Source: DMZ_SERVERS ➔ Dest: * : Ports 53, 123"),
            ("Regla 2 (Aislamiento Corp)", "DROP IPv4 * ➔ Source: DMZ_SERVERS ➔ Dest: LAN_CORP (192.168.10.0/24)"),
            ("Regla 3 (Aislamiento Mgmt)", "DROP IPv4 * ➔ Source: DMZ_SERVERS ➔ Dest: MGMT_SEC (192.168.99.0/24)"),
            ("Regla 4 (Salida Web Updates)", "PASS IPv4 TCP ➔ Source: DMZ_SERVERS ➔ Dest: * : Ports 80, 443"),
            ("Regla WAN (Acceso VIP)", "PASS IPv4 TCP ➔ Source: * ➔ Dest: WAN address : Port 443 (HAProxy VIP)"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p6_1)
    story.append(Spacer(1, 4))

    story.append(Paragraph("FASE 7: ENLACE ZERO TRUST CON TAILSCALE SUBNET ROUTER (VOIP PBX)", h1_style))
    gui_p7_1 = make_gui_mockup(
        "VPN / Tailscale / Settings",
        [
            ("Enable Tailscale Daemon", "[X] Enable Tailscale service daemon"),
            ("Authentication Key", "Auth Key: tskey-auth-k98a-*********************************"),
            ("Advertised Subnet Routes", "192.168.30.0/24 (Publica subred VoIP hacia la Tailnet privada)"),
            ("Accept Subnet Routes", "[X] Enable route passing for connected Softphones (Zoiper/Linphone)"),
            ("Tailscale Admin Action", "note:En login.tailscale.com > Machines > pfSense > Edit route settings > Aprobar 192.168.30.0/24"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(gui_p7_1)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 8: FASE 8 (VERIFICACIÓN Y DIAGNÓSTICO EN CONSOLA FREEBSD)
    # =========================================================================
    story.append(Paragraph("FASE 8: VERIFICACIÓN Y DIAGNÓSTICO EN CONSOLA FREEBSD", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=5))

    story.append(Paragraph("Para validar la operatividad total del firewall, acceder vía SSH (<code>ssh admin@192.168.99.1</code>):", body_style))
    
    code_cli_full = (
        "# 1. Verificar Suricata activo con hilos Netmap en tiempo real:\n"
        "ps aux | grep suricata\n"
        "netstat -i\n\n"
        "# 2. Tail en vivo del log de eventos EVE JSON estructurado con jq:\n"
        "tail -f /var/log/suricata/eve.json | jq '{time: .timestamp, src: .src_ip, dst: .dest_ip, alert: .alert.signature}'\n\n"
        "# 3. Comprobar la tabla de persistencia en kernel de FreeBSD (snort2c):\n"
        "pfctl -t snort2c -T show\n\n"
        "# 4. Probar atómicamente si una IP atacante está bloqueada en memoria RAM:\n"
        "pfctl -t snort2c -T test 198.51.100.100\n\n"
        "# 5. Inserción manual de prueba en la tabla de kernel:\n"
        "pfctl -t snort2c -T add 198.51.100.100\n\n"
        "# 6. Eliminar estados de conexión residuales de la IP atacante:\n"
        "pfctl -k 198.51.100.100\n\n"
        "# 7. Comprobar estado de sockets y puertos en escucha (HAProxy y Syslog):\n"
        "sockstat -4 -l"
    )
    story.append(Preformatted(code_cli_full, code_style))

    story.append(Paragraph("CONCLUSIÓN DEL DESPLIEGUE: Siguiendo este blueprint paso a paso, el firewall pfSense CE 2.9.0 queda configurado con hardening perimetral de nivel profesional, inspección de paquetes en microsegundos sin falsos positivos y orquestación de respuesta autónoma SOAR.", callout_style))

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=draw_background, onLaterPages=draw_background)
    print(f"Master Step-by-Step Tutorial PDF generated successfully: {output_filename}")

if __name__ == "__main__":
    output_pdf = "docs/TUTORIAL_PASO_A_PASO_CONFIGURACION_PFSENSE_MOCKUPS.pdf"
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    build_master_tutorial_pdf(output_pdf)
