#!/usr/bin/env python3
"""
KRONOS SENTINEL - pfSense CE 2.9.0 Step-by-Step Tutorial with WebGUI Mockup Simulation
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

# GUI Mockup Palette (Bootstrap Dark pfSense style)
GUI_HEADER_BG = colors.HexColor("#111827")
GUI_BODY_BG = colors.HexColor("#0B1120")
GUI_FIELD_BG = colors.HexColor("#1E293B")
GUI_LABEL_COLOR = colors.HexColor("#94A3B8")
GUI_VALUE_COLOR = colors.HexColor("#38BDF8")
GUI_BTN_SAVE = colors.HexColor("#2563EB")
GUI_BTN_APPLY = colors.HexColor("#059669")

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
            self.drawString(130, 762, "//  pfSense CE 2.9.0 Step-by-Step WebGUI Tutorial")
            
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
    """Generates a pfSense WebGUI UI simulated card table."""
    body_style = styles['BodyDark']
    code_style = styles['CodeSnippet']
    
    rows = []
    # Header bar (Breadcrumb)
    header_p = Paragraph(f"<b><font color='#00E5FF'>🌐 pfSense WebGUI</font></b> <font color='#64748B'>// </font><font color='#E2E8F0'>{title_path}</font>", body_style)
    rows.append([header_p, ""])
    
    for label, val in fields:
        p_label = Paragraph(f"<b><font color='#94A3B8'>{label}</font></b>", body_style)
        if isinstance(val, str) and val.startswith("btn:"):
            # Buttons row
            btn_text = val.replace("btn:", "")
            p_val = Paragraph(f"<b><font color='#38BDF8'>{btn_text}</font></b>", body_style)
        else:
            p_val = Paragraph(f"<font color='#38BDF8'><code>{val}</code></font>", body_style)
        rows.append([p_label, p_val])
        
    t = Table(rows, colWidths=[160, 372])
    t_style = [
        ('SPAN', (0,0), (1,0)),
        ('BACKGROUND', (0,0), (-1,0), GUI_HEADER_BG),
        ('BACKGROUND', (0,1), (-1,-1), GUI_BODY_BG),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#2563EB")),
        ('INNERGRID', (0,1), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]
    t.setStyle(TableStyle(t_style))
    return t

def build_tutorial_pdf(output_filename: str):
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
        fontSize=11,
        leading=14,
        textColor=CYAN_ACCENT,
        spaceBefore=6,
        spaceAfter=3
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=TEXT_HEADING,
        spaceBefore=4,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=TEXT_LIGHT,
        spaceAfter=2
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=CRIMSON_BADGE,
        spaceBefore=2,
        spaceAfter=4
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
    # PÁGINA 1: PORTADA, PASO 1 (VLANs) & PASO 2 (DHCP/STATIC MAPPINGS)
    # =========================================================================
    logo_path = "assets/sentinel_shield_logo.png"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=80, height=80))
        story.append(Spacer(1, 3))

    story.append(Paragraph("TUTORIAL PASO A PASO: CONFIGURACIÓN MAESTRA DE pfSense CE 2.9.0", title_style))
    story.append(Paragraph("SIMULACIÓN DE INTERFAZ WebGUI &amp; PARÁMETROS OFICIALES PARA KRONOS SENTINEL", subtitle_style))
    story.append(Paragraph("<b>Autor:</b> Bruno Urrea Ortiz | Duoc UC Sede San Joaquín • <b>Portafolio de Título APT122</b> ($0 CLP)", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=5))

    story.append(Paragraph("PASO 1: CONFIGURACIÓN DE TRONCAL 802.1Q Y CREACIÓN DE VLANs", h1_style))
    story.append(Paragraph("Navegar a <code>Interfaces > Assignments > VLANs</code> y crear los 4 tags de subred sobre la interfaz física:", body_style))
    
    vlan_mockup = make_gui_mockup(
        "Interfaces / VLANs / Edit",
        [
            ("Parent Interface", "vtnet1 (LAN Trunk Physical Adapter) [▼]"),
            ("VLAN Tag", "10 (Corp) | 20 (DMZ) | 30 (VoIP) | 99 (Mgmt)"),
            ("VLAN Priority", "0 (Default 802.1p Best Effort)"),
            ("Description", "VLAN_10_CORP | VLAN_20_DMZ | VLAN_30_VOIP | VLAN_99_MGMT"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(vlan_mockup)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 2: SERVIDOR DHCP Y RESERVAS ESTÁTICAS DE IP (DVWA Y ASTERISK)", h1_style))
    story.append(Paragraph("Navegar a <code>Services > DHCP Server > DMZ_SERVERS</code> para configurar la subred y reserva fija:", body_style))
    
    dhcp_mockup = make_gui_mockup(
        "Services / DHCP Server / DMZ_SERVERS (VLAN 20)",
        [
            ("Enable DHCP Server", "[X] Enable DHCP server on DMZ_SERVERS interface"),
            ("Subnet & Range", "192.168.20.0/24 | Rango dinámico: 192.168.20.100 - .199"),
            ("DNS & Gateway", "DNS: 192.168.20.1, 1.1.1.1 | Gateway: 192.168.20.1"),
            ("Static Mapping DVWA", "MAC: 02:42:c0:a8:14:32 ➔ IP Fija: 192.168.20.50 (dvwa-dmz)"),
            ("Static Mapping Asterisk", "VLAN 30 ➔ MAC: 02:42:c0:a8:1e:32 ➔ IP: 192.168.30.50"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(dhcp_mockup)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: PASO 3 (SURICATA NETMAP), PASO 4 (DROPSID) & PASO 5 (PFBLOCKER)
    # =========================================================================
    story.append(Paragraph("PASO 3: SURICATA 7.X — MODO INLINE IPS NETMAP &amp; EVE JSON", h1_style))
    story.append(Paragraph("Navegar a <code>Services > Suricata > Interfaces > Edit [WAN]</code> y activar la inspección directa en hardware:", body_style))
    
    suri_mockup = make_gui_mockup(
        "Services / Suricata / Interfaces / WAN Settings",
        [
            ("Enable Inspection", "[X] Enable Suricata inspection on this interface"),
            ("Interface Selection", "WAN (vtnet0) [▼]"),
            ("IPS Mode Selection", "( ) Legacy Mode   (X) Inline Mode (netmap framework)"),
            ("Block on Alerts", "[X] Block offenders (Hardware ring-buffer packet drop)"),
            ("EVE JSON Logging", "[X] Enable EVE JSON Log | Type: (X) FILE (/var/log/suricata/eve.json)"),
            ("EVE Event Types", "[X] Alerts (SQLi/RCE)   [X] HTTP (URI, Host, Headers)"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(suri_mockup)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 4: GESTIÓN DE FIRMAS ET OPEN Y POLÍTICA ATÓMICA dropsid.conf", h1_style))
    story.append(Paragraph("Navegar a <code>Services > Suricata > SID Mgmt</code> para convertir alertas en drops inmediatos:", body_style))
    
    sid_mockup = make_gui_mockup(
        "Services / Suricata / SID Mgmt / dropsid.conf",
        [
            ("Automatic SID Mgmt", "[X] Enable Automatic SID State Management"),
            ("Drop SID List", "dropsid.conf (pcre:emerging-sql, pcre:emerging-exploit, pcre:community-web)"),
            ("State Order", "Drop > Enable > Disable"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(sid_mockup)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 5: pfBlockerNG-devel — GEOIP MAXMIND Y LISTAS THREAT FEEDS", h1_style))
    story.append(Paragraph("Navegar a <code>Firewall > pfBlockerNG > IP > GeoIP</code> para blindaje perimetral geográfico:", body_style))
    
    pfb_mockup = make_gui_mockup(
        "Firewall / pfBlockerNG / IP / GeoIP & Threat Feeds",
        [
            ("MaxMind License Key", "1024982 / ******************** (Cuenta Comunitaria Free $0)"),
            ("Top Spammers GeoIP", "CN, RU, IR, KP, VN, NG [▼] ➔ Action: (X) Deny Inbound"),
            ("IP Feeds (C2/Malware)", "FireHOL_L1 & Spamhaus_DROP ➔ Action: Deny Inbound (Cada 4 hrs)"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(pfb_mockup)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: PASO 6 (HAPROXY), PASO 7 (RULES), PASO 8 (TAILSCALE) & CLI
    # =========================================================================
    story.append(Paragraph("PASO 6: HAPROXY 2.8+ — FRONTEND SSL Y STICK-TABLES ANTI-DOS", h1_style))
    story.append(Paragraph("Navegar a <code>Services > HAProxy > Frontend</code> y configurar rate limiting en memoria RAM:", body_style))
    
    haproxy_mockup = make_gui_mockup(
        "Services / HAProxy / Frontend / Edit: KRONOS_HTTPS_VIP",
        [
            ("Frontend & Address", "KRONOS_HTTPS_FRONTEND | WAN IP:443 (SSL Offloading)"),
            ("Stick Tables", "stick-table type ip size 100k expire 30s store http_req_rate(10s),http_err_rate(10s)"),
            ("Protección L7", "http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }"),
            ("Default Backend", "DVWA_DMZ_POOL ➔ IP: 192.168.20.50:80 (Health Check: HTTP /)"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(haproxy_mockup)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 7: TAILSCALE SUBNET ROUTER &amp; REGLAS DE FIREWALL ZERO TRUST", h1_style))
    story.append(Paragraph("Navegar a <code>VPN > Tailscale</code> y <code>Firewall > Rules</code> para aislar y conectar componentes:", body_style))
    
    vpn_mockup = make_gui_mockup(
        "VPN / Tailscale & Firewall / Rules / DMZ_SERVERS",
        [
            ("Tailscale Subnet Router", "Auth Key: tskey-auth-*** | Advertised Routes: 192.168.30.0/24 (VoIP)"),
            ("Regla DMZ 1 (DNS/NTP)", "PASS IPv4 UDP ➔ DMZ_SERVERS to * : 53, 123"),
            ("Regla DMZ 2 (Aislamiento)", "DROP IPv4 * ➔ DMZ_SERVERS to LAN_CORP (V10) & MGMT (V99)"),
            ("Regla VoIP (Asterisk)", "PASS IPv4 UDP ➔ Softphone CISO to Asterisk: 5060, 10000-10100"),
            ("Acciones WebGUI", "btn:[ Save ]   [ Apply Changes ]")
        ],
        styles
    )
    story.append(vpn_mockup)
    story.append(Spacer(1, 4))

    story.append(Paragraph("PASO 8: VERIFICACIÓN EN CONSOLA FREEBSD (CLI DE DIAGNÓSTICO)", h1_style))
    code_cli = (
        "# 1. Verificar Suricata activo con hilos Netmap:\n"
        "ps aux | grep suricata\n\n"
        "# 2. Comprobar inserción atómica en la tabla en memoria snort2c:\n"
        "pfctl -t snort2c -T show\n"
        "pfctl -t snort2c -T test 198.51.100.100\n\n"
        "# 3. Tail en vivo del log de eventos EVE JSON analizado por KRONOS Engine:\n"
        "tail -f /var/log/suricata/eve.json"
    )
    story.append(Preformatted(code_cli, code_style))

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=draw_background, onLaterPages=draw_background)
    print(f"Step-by-Step Tutorial PDF generated successfully: {output_filename}")

if __name__ == "__main__":
    output_pdf = "docs/TUTORIAL_PASO_A_PASO_CONFIGURACION_PFSENSE_MOCKUPS.pdf"
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    build_tutorial_pdf(output_pdf)
