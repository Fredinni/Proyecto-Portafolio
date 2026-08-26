#!/usr/bin/env python3
"""
KRONOS SENTINEL - IP Challenges, CGNAT & Exposure Strategies PDF Generator ($0 Cost Policy)
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
            self.drawString(130, 762, "//  IP Challenges, CGNAT & Zero-Cost ($0 CLP) Defense Report")
            
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
        fontSize=12,
        leading=15,
        textColor=CYAN_ACCENT,
        spaceBefore=8,
        spaceAfter=5
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=TEXT_HEADING,
        spaceBefore=6,
        spaceAfter=3
    )

    h3_style = ParagraphStyle(
        'SectionH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=CYAN_ACCENT,
        spaceBefore=5,
        spaceAfter=3
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
        spaceAfter=5
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
        spaceAfter=4
    )

    story = []

    # =========================================================================
    # PÁGINA 1: PORTADA, PREMISA $0 CLP & PROBLEMÁTICAS IDENTIFICADAS
    # =========================================================================
    logo_path = "assets/sentinel_shield_logo.png"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=95, height=95))
        story.append(Spacer(1, 4))

    story.append(Paragraph("INFORME TÉCNICO: PROBLEMÁTICAS DE DIRECCIONAMIENTO IP, CGNAT Y EXPOSICIÓN WAN ($0 COSTO)", title_style))
    story.append(Paragraph("ANÁLISIS DE FACTIBILIDAD Y ESTRATEGIAS DE DEFENSA PRESENCIAL // DUOC UC APT122", subtitle_style))
    story.append(Paragraph("<b>Autor:</b> Bruno Urrea Ortiz | Escuela de Informática y Telecomunicaciones — Duoc UC Sede San Joaquín<br/><b>Premisa Financiera:</b> Arquitectura 100% Costo Cero ($0 CLP) mediante Open Source y Capas Gratuitas (Free Tiers)", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=6))

    story.append(Paragraph("1. PREMISA DE ARQUITECTURA DE COSTO CERO ($0 CLP)", h1_style))
    story.append(Paragraph("El proyecto <b>KRONOS SENTINEL</b> ha sido diseñado bajo una estricta directriz de costo cero ($0 CLP), aprovechando recursos comunitarios y capas gratuitas de computación e Inteligencia Artificial:", body_style))
    story.append(Paragraph("• <b>Google Gemini Live API Flash 3.1:</b> Capa gratuita de Google AI Studio para streaming de audio bidireccional.<br/>"
                           "• <b>pfSense CE 2.7.2 & FreeBSD 14:</b> Sistema operativo y firewall perimetral Open Source ($0).<br/>"
                           "• <b>Suricata 7.x & ET Open:</b> Motor de prevención de intrusiones y firmas comunitarias ($0).<br/>"
                           "• <b>Asterisk 20 LTS PBX & HAProxy:</b> Telefonía VoIP y balanceo inverso en contenedores Docker ($0).<br/>"
                           "• <b>Tailscale Free Community:</b> Red mesh WireGuard Zero Trust gratuita hasta 100 nodos ($0).<br/>"
                           "• <b>Conectividad:</b> Hotspot 4G/5G de smartphone personal o conexión cableada RJ45 en laboratorios de Duoc UC ($0).", body_style))

    story.append(Paragraph("2. MATRIZ DE PROBLEMÁTICAS TÉCNICAS EN REDES DOMÉSTICAS Y SEDE DUOC UC", h1_style))
    story.append(Paragraph("<b>A. Carrier-Grade NAT (CGNAT / RFC 6598 - 100.64.0.0/10):</b> Los ISP residenciales en Chile (Movistar, Entel, VTR, Mundo) y operadores 4G/5G asignan IPs privadas compartidas en lugar de IPv4 públicas. El reenvío de puertos tradicional no funciona hacia el exterior.", body_style))
    story.append(Paragraph("<b>B. Doble NAT y Bloqueo RFC 1918 en pfSense:</b> Al conectar la WAN de pfSense al router del hogar o tethering, pfSense descarta por defecto paquetes privados. En <b>Interfaces > WAN</b> se debe desmarcar <code>Block private networks and loopback addresses</code>.", body_style))
    story.append(Paragraph("<b>C. Aislamiento de Clientes en Red Sede Duoc UC:</b> Los switches de los laboratorios aplican <i>Client Isolation</i> y filtrado de escaneos, impidiendo ataques directos entre dos notebooks en la misma sala sin un laboratorio virtual cerrado.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: ANÁLISIS COMPARATIVO DE OPCIONES PARA LA DEFENSA PRESENCIAL
    # =========================================================================
    story.append(Paragraph("3. MATRIZ COMPARATIVA DE OPCIONES PARA LA DEFENSA PRESENCIAL", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=6))

    comp_table_data = [
        [Paragraph("<b>Opción</b>", body_style), Paragraph("<b>Mecanismo Técnico</b>", body_style), Paragraph("<b>Costo</b>", body_style), Paragraph("<b>Riesgo en Vivo</b>", body_style), Paragraph("<b>Veredicto</b>", body_style)],
        [Paragraph("<b>1. Lab Virtual + Hotspot 4G/5G</b>", body_style), Paragraph("Ataque local (198.51.100.0/24) + Salida 443 a Gemini Live.", body_style), Paragraph("<b>$0 CLP</b>", body_style), Paragraph("<b>Casi Nulo (< 1%)</b>", body_style), Paragraph("<b>ESTÁNDAR DE ORO (Recomendada)</b>", body_style)],
        [Paragraph("<b>2. Cloudflare Zero Trust Tunnel</b>", body_style), Paragraph("cloudflared tunnel a DMZ + Hotspot 4G/5G.", body_style), Paragraph("<b>$0 CLP</b>", body_style), Paragraph("Medio (15% por lag 4G)", body_style), Paragraph("Viable para acceso de profesores.", body_style)],
        [Paragraph("<b>3. Tailscale Subnet Router</b>", body_style), Paragraph("Red Mesh WireGuard para Softphone CISO (VLAN 30).", body_style), Paragraph("<b>$0 CLP</b>", body_style), Paragraph("Bajo (5%)", body_style), Paragraph("<b>Óptima para llamadas PBX.</b>", body_style)],
        [Paragraph("<b>4. Conexión Directa RJ45 Duoc</b>", body_style), Paragraph("pfSense WAN a switch de la sede + NAT alumno.", body_style), Paragraph("<b>$0 CLP</b>", body_style), Paragraph("Alto (> 50% bloqueo)", body_style), Paragraph("No recomendada para el ataque.", body_style)]
    ]
    t_comp = Table(comp_table_data, colWidths=[105, 172, 50, 85, 120])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#0D1527"), colors.HexColor("#090D1A")]),
        ('TEXTCOLOR', (0,0), (-1,0), CYAN_ACCENT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, CYAN_ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_comp)

    story.append(Spacer(1, 8))
    story.append(Paragraph("4. DESGLOSE DETALLADO DE PROS & CONTRAS POR ESCENARIO", h1_style))

    story.append(Paragraph("OPCIÓN 1: LABORATORIO VIRTUAL AUTÓNOMO DUAL-HOST + HOTSPOT 4G/5G (RECOMENDADA)", h2_style))
    story.append(Paragraph("• <b>Arquitectura:</b> Kali Linux (198.51.100.100) y pfSense WAN (198.51.100.1) conviven en un vSwitch aislado dentro del notebook. El tráfico de ataque SQLi corre localmente con 0ms de lag.<br/>"
                           "• <b>Integración IA:</b> pfSense / Python conecta a Internet mediante el Hotspot 4G/5G del celular (o cable RJ45) <b>únicamente para la conexión saliente HTTPS/WSS (puerto 443) hacia Google Gemini Live API Flash 3.1</b>.<br/>"
                           "• <b>PROS:</b> Costo $0 CLP, 100% inmune a CGNAT (conexión saliente), cero dependencia del Wi-Fi de la sede, demostración determinista en tiempo real (< 150ms).<br/>"
                           "• <b>CONTRAS:</b> Requiere notebook con 16 GB de RAM para ejecutar las máquinas virtuales simultáneamente.", body_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("OPCIÓN 2: CLOUDFLARE ZERO TRUST TUNNEL (FREE TIER)", h2_style))
    story.append(Paragraph("• <b>Arquitectura:</b> Se ejecuta el demonio <code>cloudflared</code> en pfSense, publicando HAProxy hacia un subdominio público.<br/>"
                           "• <b>PROS:</b> Permite que la comisión evaluadora ingrese a la web vulnerable desde sus propios teléfonos móviles.<br/>"
                           "• <b>CONTRAS:</b> Depende de la estabilidad de la señal celular 4G en la sala durante el escaneo en vivo.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: TAILSCALE & BLUEPRINT FINAL DE TITULACIÓN
    # =========================================================================
    story.append(Paragraph("OPCIÓN 3: TAILSCALE SUBNET ROUTER PARA ASTERISK PBX Y SOFTPHONE CISO", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=6))
    story.append(Paragraph("• <b>Arquitectura:</b> Paquete <code>pfSense-pkg-tailscale</code> activo publicando la ruta <code>192.168.30.0/24</code> (VLAN VoIP). El smartphone del CISO se conecta a la Tailnet privada y registra Zoiper con el anexo 1001.<br/>"
                           "• <b>PROS:</b> Costo $0 CLP, cifrado E2E WireGuard nativo, atraviesa cualquier NAT/CGNAT mediante STUN/DERP sin abrir puertos SIP (5060 UDP) a Internet.<br/>"
                           "• <b>CONTRAS:</b> Requiere instalar la app Tailscale en el teléfono del evaluador/CISO.", body_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("5. BLUEPRINT OPERATIVO PARA EL DÍA DE LA DEFENSA EN DUOC UC", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN_ACCENT, spaceAfter=6))
    story.append(Paragraph("El equipo de desarrollo implementará el <b>Modelo Híbrido Resiliente de $0 Costo</b>:", body_style))
    story.append(Paragraph("<b>1. Fase de Ataque e Ingesta (100% Local y Determinista):</b><br/>"
                           "Se dispara el ataque desde la VM Kali Linux local contra el Frontend HAProxy de pfSense. Suricata en modo Inline Netmap descarta los paquetes maliciosos y <code>pfctl</code> bloquea la IP en el kernel en menos de 100 milisegundos sin riesgo de fallas externas.<br/>"
                           "<b>2. Fase de Notificación y Voz IA (Conexión Saliente 443):</b><br/>"
                           "El demonio KRONOS abre el WebSocket saliente hacia <b>Google Gemini Live API Flash 3.1</b> utilizando el tethering 4G/5G del smartphone personal o el cable de red de la sede.<br/>"
                           "<b>3. Fase de Audio en Vivo frente a la Comisión:</b><br/>"
                           "Asterisk PBX genera la llamada telefónica al Softphone CISO (vía Tailscale o anexo local en la laptop con altavoces activados), permitiendo a toda la comisión examinadora escuchar el reporte de voz interactivo de la IA en tiempo real.", body_style))

    story.append(Paragraph("CONCLUSIÓN: Esta arquitectura garantiza el 100% de cumplimiento técnico, costo cero de despliegue ($0 CLP) y máxima estabilidad operativa durante la defensa presencial de título.", callout_style))

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=draw_background, onLaterPages=draw_background)
    print(f"IP Challenges and Zero-Cost Defense PDF generated successfully: {output_filename}")

if __name__ == "__main__":
    output_pdf = "docs/PROBLEMATICAS_ENCONTRADAS_IP_Y_ALTERNATIVAS_EXPOSICION.pdf"
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    build_ip_problems_pdf(output_pdf)
