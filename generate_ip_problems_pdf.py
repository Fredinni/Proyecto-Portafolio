#!/usr/bin/env python3
"""
KRONOS SENTINEL - IP Challenges, CGNAT & Exposure Strategies PDF Generator
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
            self.drawString(130, 762, "//  IP Challenges, CGNAT & WAN Exposure Report")
            
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

def build_ip_problems_pdf(output_filename: str):
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
        fontSize=20,
        leading=24,
        textColor=TEXT_HEADING,
        alignment=1,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=CYAN_ACCENT,
        alignment=1,
        spaceAfter=4
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_MUTED,
        alignment=1,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=CYAN_ACCENT,
        spaceBefore=10,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=TEXT_HEADING,
        spaceBefore=8,
        spaceAfter=4
    )

    h3_style = ParagraphStyle(
        'SectionH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=CYAN_ACCENT,
        spaceBefore=6,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=TEXT_LIGHT,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=CRIMSON_BADGE,
        spaceBefore=4,
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=CODE_TEXT,
        backColor=CODE_BG,
        borderColor=BORDER_COLOR,
        borderWidth=0.5,
        borderPadding=5,
        spaceBefore=3,
        spaceAfter=5
    )

    story = []

    # =========================================================================
    # PÁGINA 1: PORTADA & PROBLEMÁTICAS IDENTIFICADAS
    # =========================================================================
    logo_path = "assets/sentinel_shield_logo.png"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=110, height=110))
        story.append(Spacer(1, 6))

    story.append(Paragraph("INFORME TÉCNICO: PROBLEMÁTICAS DE DIRECCIONAMIENTO IP, CGNAT Y EXPOSICIÓN WAN", title_style))
    story.append(Paragraph("ANÁLISIS DE FACTIBILIDAD Y ESTRATEGIAS DE CONECTIVIDAD // KRONOS SENTINEL", subtitle_style))
    story.append(Paragraph("<b>Autor:</b> Bruno Urrea Ortiz | Escuela de Informática y Telecomunicaciones — Duoc UC Sede San Joaquín<br/><b>Proyecto:</b> Portafolio de Título (APT122) • Clasificación: Ingeniería de Infraestructura & Ciberseguridad", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=8))

    story.append(Paragraph("1. RESUMEN EJECUTIVO Y DESAFÍO DE INFRAESTRUCTURA", h1_style))
    story.append(Paragraph("Para validar la capacidad de respuesta autónoma de <b>KRONOS SENTINEL</b> ante vectores de ataque reales (inyecciones SQL, escaneos L7), el servicio web expuesto por <b>HAProxy en DMZ</b> debe ser accesible desde la Internet pública. Al virtualizar el entorno en una red doméstica o notebook, surgen desafíos críticos en la capa de red provocados por los Proveedores de Servicios de Internet (ISP) en Chile (Movistar, Entel, VTR, Mundo):", body_style))

    story.append(Paragraph("2. MATRIZ DE PROBLEMÁTICAS TÉCNICAS EN REDES RESIDENCIALES", h1_style))
    
    story.append(Paragraph("<b>A. Carrier-Grade NAT (CGNAT / RFC 6598 - 100.64.0.0/10):</b><br/>"
                           "La mayoría de las conexiones residenciales no reciben una IPv4 pública en el router ONT/HGU, sino una dirección privada compartida mediante CGNAT. Esto anula por completo el reenvío de puertos (<i>Port Forwarding</i>), ya que el router de borde del ISP descarta cualquier paquete entrante no solicitado.", body_style))

    story.append(Paragraph("<b>B. Doble NAT y Bloqueo RFC 1918 en la WAN de pfSense:</b><br/>"
                           "Al conectar la interfaz WAN de pfSense al router del hogar (recibiendo ej. <code>192.168.1.200</code>), pfSense activa por defecto la regla <code>Block private networks and loopback addresses</code>, descartando silenciosamente todo el tráfico reenviado por el router del hogar.", body_style))

    story.append(Paragraph("<b>C. Bloqueo de Puertos Canónicos en Planes Hogar:</b><br/>"
                           "Los ISP suelen filtrar puertos de entrada conocidos (TCP 80, 443, 25 y UDP 5060 de SIP) para evitar el hosting de servidores web o centrales telefónicas no autorizadas en enlaces residenciales.", body_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Comandos de Diagnóstico y Comprobación de CGNAT en CLI:", h3_style))
    code_diag = (
        "# 1. Consultar IP pública real vista desde Internet:\n"
        "curl -s https://ifconfig.me\n\n"
        "# 2. Comparar con la IP asignada en la WAN del router ISP:\n"
        "# Si la IP WAN inicia con 100.64.x.x -> Tu conexión se encuentra bajo CGNAT.\n\n"
        "# 3. Trazado de ruta hacia DNS para detectar salto CGNAT intermedio:\n"
        "traceroute -n -m 4 1.1.1.1"
    )
    story.append(Preformatted(code_diag, code_style))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: ANÁLISIS COMPARATIVO DE ALTERNATIVAS DE EXPOSICIÓN
    # =========================================================================
    story.append(Paragraph("3. MATRIZ COMPARATIVA DE ALTERNATIVAS DE EXPOSICIÓN", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=8))

    comp_table_data = [
        [Paragraph("<b>Alternativa</b>", body_style), Paragraph("<b>Mecanismo Técnico</b>", body_style), Paragraph("<b>Viabilidad</b>", body_style), Paragraph("<b>Complejidad</b>", body_style), Paragraph("<b>Dependencia ISP</b>", body_style)],
        [Paragraph("<b>Opción A: Modo Puente (Bridge)</b>", body_style), Paragraph("ONT en monopuesto + PPPoE/DHCP en WAN pfSense.", body_style), Paragraph("Media", body_style), Paragraph("Media", body_style), Paragraph("Alta (Requiere ISP sin CGNAT)", body_style)],
        [Paragraph("<b>Opción B: DMZ en Router Hogar</b>", body_style), Paragraph("DMZ a IP WAN pfSense + Desactivar RFC 1918.", body_style), Paragraph("Alta", body_style), Paragraph("Baja", body_style), Paragraph("Media (Requiere acceso a ONT)", body_style)],
        [Paragraph("<b>Opción C: Cloud VPS WireGuard</b>", body_style), Paragraph("Relay en VPS público + Túnel WireGuard a pfSense.", body_style), Paragraph("<b>Máxima</b>", body_style), Paragraph("Media", body_style), Paragraph("<b>Nula (Bypass total CGNAT)</b>", body_style)],
        [Paragraph("<b>Opción D: Tailscale Subnet Router</b>", body_style), Paragraph("Red Mesh WireGuard para VoIP Asterisk y CISO.", body_style), Paragraph("<b>Máxima</b>", body_style), Paragraph("Baja", body_style), Paragraph("<b>Nula (Cifrado E2E nativo)</b>", body_style)],
        [Paragraph("<b>Opción E: Laboratorio Autónomo</b>", body_style), Paragraph("Simulación WAN con VM Kali en Proxmox/VMware.", body_style), Paragraph("<b>Máxima</b>", body_style), Paragraph("Baja", body_style), Paragraph("<b>Nula (Ideal Defensa Duoc)</b>", body_style)]
    ]
    t_comp = Table(comp_table_data, colWidths=[110, 162, 70, 75, 115])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#0D1527"), colors.HexColor("#090D1A")]),
        ('TEXTCOLOR', (0,0), (-1,0), CYAN_ACCENT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, CYAN_ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_comp)

    story.append(Spacer(1, 10))
    story.append(Paragraph("4. GUÍA DE IMPLEMENTACIÓN POR ESCENARIO", h1_style))
    
    story.append(Paragraph("ESCENARIO 1: DMZ HOST Y BYPASS DE DOBLE NAT EN EL HOGAR (OPCIÓN B)", h2_style))
    story.append(Paragraph("Si se mantiene el router del ISP enrutando normalmente hacia el hogar:", body_style))
    story.append(Paragraph("<b>1. IP Estática WAN:</b> En pfSense (<b>Interfaces > WAN</b>), asignar IP estática fija (ej. <code>192.168.1.200/24</code>) con Gateway <code>192.168.1.1</code>.<br/>"
                           "<b>2. Desactivar Bloqueo RFC 1918:</b> En <b>Interfaces > WAN</b>, desmarcar obligatoriamente <code>Block private networks and loopback addresses</code> y <code>Block bogon networks</code>. <i>(Paso indispensable para recibir tráfico)</i>.<br/>"
                           "<b>3. Configuración DMZ:</b> En la administración del router ISP, configurar DMZ Host apuntando a la IP <code>192.168.1.200</code>.", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("ESCENARIO 2: CLOUD RELAY CON TÚNEL WIREGUARD (OPCIÓN C - BYPASS TOTAL CGNAT)", h2_style))
    story.append(Paragraph("Para garantizar acceso público cuando el ISP aplica CGNAT estricto sin posibilidad de apertura de puertos:", body_style))
    story.append(Paragraph("• Se despliega un VPS en la nube con IPv4 pública estática fija (Oracle Free Tier / DigitalOcean).<br/>"
                           "• Se establece un túnel WireGuard punto a punto entre el VPS (<code>10.50.0.1</code>) y pfSense (<code>10.50.0.2</code>).<br/>"
                           "• El VPS reenvía las peticiones HTTP/HTTPS entrantes mediante <code>iptables PREROUTING</code> a través del túnel directamente hacia HAProxy en pfSense.", body_style))

    code_wg_vps = (
        "# Reglas iptables en el VPS en la nube para reenvío WAN a través del túnel:\n"
        "sysctl -w net.ipv4.ip_forward=1\n"
        "iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.50.0.2:80\n"
        "iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination 10.50.0.2:443\n"
        "iptables -t nat -A POSTROUTING -o wg0 -j MASQUERADE"
    )
    story.append(Preformatted(code_wg_vps, code_style))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: INTEGRACIÓN TAILSCALE SUBNET ROUTER & LAB DUOC UC
    # =========================================================================
    story.append(Paragraph("5. INTEGRACIÓN DE TAILSCALE SUBNET ROUTER EN pfSense PARA ASTERISK PBX", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=8))

    story.append(Paragraph("Para conectar el Softphone del CISO (en smartphone o notebook) con Asterisk PBX sin exponer puertos SIP (5060 UDP) o RTP a Internet:", body_style))
    story.append(Paragraph("<b>1. Instalación del Paquete:</b> En pfSense (<b>System > Package Manager</b>), instalar <code>pfSense-pkg-tailscale</code>.<br/>"
                           "<b>2. Publicación de Subred (Subnet Router):</b> En <b>VPN > Tailscale</b>, ingresar la clave de autenticación (*Auth Key*) y en <b>Advertised Routes</b> declarar la subred de telefonía VoIP: <code>192.168.30.0/24</code>.<br/>"
                           "<b>3. Aprobación en Consola Admin:</b> En el panel de control de Tailscale, acceder a <i>Machines > pfSense > Edit route settings</i> y autorizar la subred <code>192.168.30.0/24</code>.<br/>"
                           "<b>4. Registro del Softphone:</b> El CISO activa Tailscale en su equipo y configura su softphone (Zoiper/Linphone) apuntando directamente a la IP privada <code>192.168.30.50</code> (Anexo 1001), logrando audio bidireccional cifrado de ultrabaja latencia sin atravesar CGNAT.", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("6. ENTORNO DE LABORATORIO AUTÓNOMO PARA DEFENSA EN DUOC UC (OPCIÓN E)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=8))

    story.append(Paragraph("Para la presentación final presencial frente a la comisión evaluadora de Duoc UC, se implementa una topología virtual 100% aislada:", body_style))
    story.append(Paragraph("• <b>Switch Virtual WAN Aislado (<code>vmbr1</code> / <code>VMnet2</code>):</b> Red pública simulada <code>198.51.100.0/24</code>.<br/>"
                           "• <b>pfSense WAN IP:</b> <code>198.51.100.1/24</code> | <b>VM Atacante (Kali Linux):</b> <code>198.51.100.100/24</code>.<br/>"
                           "• <b>Ejecución de Prueba en Vivo:</b> Desde Kali Linux se dispara el exploit SQLi contra HAProxy:<br/>"
                           "  <code>sqlmap -u \"https://198.51.100.1/vulnerabilities/sqli/?id=1&Submit=Submit\" --cookie=\"...\" --batch</code><br/>"
                           "• Suricata en pfSense intercepta el ataque en modo Inline Netmap, <code>pfctl</code> bloquea la IP en el kernel, Asterisk dispara la llamada al softphone del CISO y el <b>Agente Gemini Live Flash 3.1</b> ejecuta el debriefing por voz en tiempo real.", body_style))

    story.append(Paragraph("RECOMENDACIÓN FINAL: Para el desarrollo diario utilizar la combinación de Cloud VPS Relay (Web HAProxy) + Tailscale Subnet Router (VoIP PBX). Para la defensa presencial de título, utilizar el Laboratorio Virtual Autónomo para garantizar latencia cero y cero dependencia de conexiones externas.", callout_style))

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=draw_background, onLaterPages=draw_background)
    print(f"IP Challenges and Exposure PDF generated successfully: {output_filename}")

if __name__ == "__main__":
    output_pdf = "docs/PROBLEMATICAS_ENCONTRADAS_IP_Y_ALTERNATIVAS_EXPOSICION.pdf"
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    build_ip_problems_pdf(output_pdf)
