#!/usr/bin/env python3
"""
Generador Maestro de Presentación PDF 16:9 Landscape - Fase 1: Definición Proyecto APT
Asignatura: Portafolio de Título (APT122) - Duoc UC Sede San Joaquín
Proyecto: KRONOS SENTINEL - Autonomous AI-IPS & Real-Time Incident Voice Response SOAR Architecture
Tema: Lo-Fi Cyberpunk Purple Waves / Glassmorphic Deep Purple / 16:9 Widescreen
"""

import os
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, Image
from reportlab.pdfgen import canvas

OUTPUT_DIR = "docs/Fase_1_Definicion_Proyecto_APT"
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "Presentacion_Proyecto_APT_Fase1_KRONOS_SENTINEL.pdf")
BG_IMAGE_PATH = "assets/lofi_purple_waves_bg.png"

PAGE_W = 960.0
PAGE_H = 540.0
PAGE_SIZE = (PAGE_W, PAGE_H)

# Paleta Cromática Lo-Fi Purple
BG_DARK = colors.HexColor("#080412")
CARD_BG = colors.HexColor("#140B29")
CARD_HDR_BG = colors.HexColor("#231448")
BORDER_C = colors.HexColor("#4C1D95")
BORDER_LIGHT = colors.HexColor("#7C3AED")

CYAN_C = colors.HexColor("#00F0FF")
SKY_C = colors.HexColor("#38BDF8")
RED_C = colors.HexColor("#F87171")
AMBER_C = colors.HexColor("#FBBF24")
GREEN_C = colors.HexColor("#34D399")
PURPLE_C = colors.HexColor("#C084FC")
PINK_C = colors.HexColor("#F472B6")

TEXT_W = colors.HexColor("#FFFFFF")
TEXT_L = colors.HexColor("#EDE9FE")
TEXT_M = colors.HexColor("#C4B5FD")
TEXT_D = colors.HexColor("#8B5CF6")

class LoFiSlideCanvas(canvas.Canvas):
    """Canvas de dos pasadas que dibuja el fondo panorámico Lo-Fi Purple Waves y la numeración."""
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
            self.draw_lofi_frame(num_pages)
            super().showPage()
        super().save()

    def draw_lofi_frame(self, total_pages):
        self.saveState()
        
        # 1. Dibujar imagen de fondo Lo-Fi Purple Waves si existe
        if os.path.exists(BG_IMAGE_PATH):
            self.drawImage(BG_IMAGE_PATH, 0, 0, width=PAGE_W, height=PAGE_H, preserveAspectRatio=False)
        else:
            self.setFillColor(BG_DARK)
            self.rect(0, 0, PAGE_W, PAGE_H, fill=True, stroke=False)
        
        # 2. Marco sutil con acentos neón violeta
        self.setStrokeColor(BORDER_C)
        self.setLineWidth(0.8)
        self.rect(20, 16, PAGE_W - 40, PAGE_H - 32, fill=False, stroke=True)
        
        # 3. Retículas / Crosshairs de esquina (Cyan)
        self.setStrokeColor(CYAN_C)
        self.setLineWidth(1.0)
        self.line(20, PAGE_H - 16, 32, PAGE_H - 16)
        self.line(20, PAGE_H - 16, 20, PAGE_H - 28)
        self.line(PAGE_W - 32, PAGE_H - 16, PAGE_W - 20, PAGE_H - 16)
        self.line(PAGE_W - 20, PAGE_H - 16, PAGE_W - 20, PAGE_H - 28)
        self.line(20, 16, 32, 16)
        self.line(20, 16, 20, 28)
        self.line(PAGE_W - 32, 16, PAGE_W - 20, 16)
        self.line(PAGE_W - 20, 16, PAGE_W - 20, 28)

        # 4. Línea separadora del Footer institucional
        self.setStrokeColor(BORDER_C)
        self.setLineWidth(0.5)
        self.line(36, 28, PAGE_W - 36, 28)

        # 5. Textos del Footer
        self.setFont("Helvetica-Bold", 7.0)
        self.setFillColor(CYAN_C)
        self.drawString(36, 18, "DUOC UC SAN JOAQUÍN")
        
        self.setFont("Helvetica", 7.0)
        self.setFillColor(TEXT_D)
        self.drawString(136, 18, "// Escuela de Informática y Telecomunicaciones • KRONOS SENTINEL (APT122)")
        
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(SKY_C)
        self.drawRightString(PAGE_W - 36, 18, f"SLIDE {self._pageNumber:02d} / {total_pages:02d}")
        
        self.restoreState()

def build_pdf_slides():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=PAGE_SIZE,
        leftMargin=36,
        rightMargin=36,
        topMargin=22,
        bottomMargin=34
    )

    st_title_portada = ParagraphStyle('TP', fontName='Helvetica-Bold', fontSize=22, leading=25, textColor=TEXT_W)
    st_sub_portada = ParagraphStyle('SP', fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=SKY_C)
    st_badge = ParagraphStyle('BDG', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=CYAN_C)
    
    st_header_slide = ParagraphStyle('HS', fontName='Helvetica-Bold', fontSize=14.5, leading=17.5, textColor=TEXT_W)
    st_cat_slide = ParagraphStyle('CS', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=CYAN_C)
    
    st_card_hdr = ParagraphStyle('CH', fontName='Helvetica-Bold', fontSize=8.5, leading=10.5, textColor=CYAN_C)
    st_card_hdr_sky = ParagraphStyle('CHS', fontName='Helvetica-Bold', fontSize=8.5, leading=10.5, textColor=SKY_C)
    st_card_hdr_green = ParagraphStyle('CHG', fontName='Helvetica-Bold', fontSize=8.5, leading=10.5, textColor=GREEN_C)
    st_card_hdr_amber = ParagraphStyle('CHA', fontName='Helvetica-Bold', fontSize=8.5, leading=10.5, textColor=AMBER_C)
    st_card_hdr_red = ParagraphStyle('CHR', fontName='Helvetica-Bold', fontSize=8.5, leading=10.5, textColor=RED_C)
    
    st_body = ParagraphStyle('B', fontName='Helvetica', fontSize=7.6, leading=10.2, textColor=TEXT_L)
    st_body_bold = ParagraphStyle('BB', fontName='Helvetica-Bold', fontSize=7.8, leading=10.5, textColor=TEXT_W)
    st_muted = ParagraphStyle('BM', fontName='Helvetica', fontSize=7.0, leading=9.2, textColor=TEXT_M)
    st_center = ParagraphStyle('BC', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=TEXT_L, alignment=1)

    story = []

    def slide_header(category, title):
        story.append(Paragraph(f"[ {category.upper()} ]", st_cat_slide))
        story.append(Spacer(1, 2))
        story.append(Paragraph(title, st_header_slide))
        story.append(Spacer(1, 3))
        story.append(HRFlowable(width="100%", thickness=0.75, color=CYAN_C, spaceAfter=7, spaceBefore=1))

    # SLIDE 1: PORTADA
    story.append(Spacer(1, 4))
    story.append(Paragraph("PORTAFOLIO DE TÍTULO (APT122) • FASE 1: DEFINICIÓN DE PROYECTO", st_badge))
    story.append(Spacer(1, 4))
    story.append(Paragraph("KRONOS SENTINEL", st_title_portada))
    story.append(Paragraph("Autonomous AI-IPS & Real-Time Incident Voice Response SOAR Architecture", st_sub_portada))
    story.append(Spacer(1, 10))

    logo_path = "assets/sentinel_shield_logo.png"
    logo_img = Image(logo_path, width=95, height=95) if os.path.exists(logo_path) else Paragraph("<b>[LOGO]</b>", st_card_hdr)

    acad_table_data = [
        [
            Paragraph("EMBLEMA", st_card_hdr),
            Paragraph("DATOS ACADÉMICOS INSTITUCIONALES", st_card_hdr_sky),
            Paragraph("EQUIPO DE INGENIERÍA Y ROLES", st_card_hdr_green)
        ],
        [
            logo_img,
            Paragraph("<b>Institución:</b> Duoc UC — Sede San Joaquín<br/><b>Escuela:</b> Informática y Telecomunicaciones<br/><b>Carrera:</b> Ingeniería en Conectividad y Redes<br/><b>Asignatura:</b> Portafolio de Título (APT122)<br/><b>Estudiante:</b> Bruno Urrea Ortiz (RUT: 21.543.637-3)<br/><b>Fecha:</b> 8 de Septiembre de 2026", st_body),
            Paragraph("• <b>Bruno Urrea Ortiz:</b> Líder Ciberseguridad, Motor KRONOS & Gemini Live<br/>• <b>Freddy Vásquez Cortés:</b> Ingeniería de Routing, Switching L2/L3 & Asterisk PBX<br/>• <b>Cristóbal Quezada:</b> Servicios Web, Proxy Inverso HAProxy SSL & DMZ DVWA<br/>• <b>Kevin Retamales:</b> Hardening Perimetral, Inteligencia pfBlockerNG & QA", st_body)
        ]
    ]
    t_s1 = Table(acad_table_data, colWidths=[110, 384, 384])
    t_s1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('ALIGN', (0,1), (0,1), 'CENTER'),
        ('VALIGN', (0,1), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_s1)
    story.append(PageBreak())

    # SLIDE 2: AGENDA
    slide_header("Estructura de la Presentación", "Agenda de la Exposición (10 Secciones)")
    agenda_data = [
        [Paragraph("SECCIONES 01 A 05 (FUNDAMENTACIÓN)", st_card_hdr), Paragraph("SECCIONES 06 A 10 (INGENIERÍA & EJECUCIÓN)", st_card_hdr_sky)],
        [
            Paragraph(
                "<b>01. Contexto y Problemática:</b> Crisis de falsos positivos (>50%) y colapso cognitivo del analista.<br/>"
                "<b>02. Descripción del Proyecto:</b> Defensa activa SOAR a costo $0 CLP y contención atómica.<br/>"
                "<b>03. Vínculo con Perfil de Egreso:</b> Mapeo de 6 competencias troncales de Conectividad y Redes.<br/>"
                "<b>04. Intereses Profesionales:</b> Especialización en Ciberseguridad Defensiva y SecOps.<br/>"
                "<b>05. Factibilidad y Riesgos:</b> Temporalidad semestral, recursos Open Source y evasión CGNAT.",
                st_body
            ),
            Paragraph(
                "<b>06. Objetivos General y Específicos:</b> 8 metas técnicas de ingeniería cuantificables.<br/>"
                "<b>07. Metodología y Roles:</b> Ciclo iterativo e incremental de 4 fases operativas.<br/>"
                "<b>08. Evidencias Comprometidas:</b> Entregables de avance, código IaC y demostración en vivo.<br/>"
                "<b>09. Plan de Trabajo y Carta Gantt:</b> Cronograma de 18 semanas de desarrollo.<br/>"
                "<b>10. Cierre y Próximos Pasos:</b> Hitos de Fase 2 y ronda de consultas con la comisión.",
                st_body
            )
        ]
    ]
    t_s2 = Table(agenda_data, colWidths=[436, 444])
    t_s2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_s2)
    story.append(PageBreak())

    # SLIDE 3: PROBLEMÁTICA & DIAGRAMA PFCTL
    slide_header("Justificación de la Problemática", "Contexto, Problemática & Diagrama de Mitigación en Kernel")
    pfctl_img_path = "assets/pfctl_decision_flow.png"
    pfctl_flowable = Image(pfctl_img_path, width=440, height=250) if os.path.exists(pfctl_img_path) else Paragraph("<i>[pfctl_decision_flow.png]</i>", st_muted)

    prob_left_data = [
        [Paragraph("1. CRISIS DE FALSOS POSITIVOS (>50%)", st_card_hdr_red)],
        [Paragraph("• Motores IPS tradicionales generan 40-60% de alertas ruidosas.<br/>• <b>Efecto:</b> Fatiga de alertas en el SOC y desatención de ataques críticos.", st_body)],
        [Paragraph("2. COLAPSO COGNITIVO BAJO PRESIÓN", st_card_hdr_red)],
        [Paragraph("• Visión de túnel ante ataques SQLi/RCE: no se puede aislar y llamar a la vez.<br/>• <b>Efecto:</b> Errores de digitación en CLI y latencia de horas en mitigación.", st_body)],
        [Paragraph("PROPUESTA DE VALOR KRONOS", st_card_hdr_green)],
        [Paragraph("• <b>Dualidad:</b> Contención en kernel (&lt;100ms) + Llamada interactiva IA (&lt;1.5s).", st_body)]
    ]
    t_p_left = Table(prob_left_data, colWidths=[430])
    t_p_left.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,2), (-1,2), CARD_HDR_BG),
        ('BACKGROUND', (0,4), (-1,4), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,1), CARD_BG),
        ('BACKGROUND', (0,3), (-1,3), CARD_BG),
        ('BACKGROUND', (0,5), (-1,5), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))

    t_p_right_data = [
        [Paragraph("DIAGRAMA TEÓRICO: SUPRESIÓN DE RUIDO & VERIFICACIÓN KERNEL", st_card_hdr_sky)],
        [pfctl_flowable]
    ]
    t_p_right = Table(t_p_right_data, colWidths=[442])
    t_p_right.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('ALIGN', (0,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,1), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))

    t_s3 = Table([[t_p_left, t_p_right]], colWidths=[436, 444])
    t_s3.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_s3)
    story.append(PageBreak())

    # SLIDE 4: DESCRIPCIÓN & ARQUITECTURA
    slide_header("Defensa en Profundidad & SOAR", "Descripción del Proyecto KRONOS SENTINEL & Arquitectura")
    arch_img_path = "assets/architecture_diagram.png"
    arch_flowable = Image(arch_img_path, width=460, height=250) if os.path.exists(arch_img_path) else Paragraph("<i>[architecture_diagram.png]</i>", st_muted)

    desc_left_data = [
        [Paragraph("OBJETIVO GENERAL EN UNA FRASE", st_card_hdr)],
        [Paragraph("<i>“Arquitectura SOAR autónoma de costo $0 CLP que contiene intrusiones en kernel FreeBSD en microsegundos e interactúa por voz con el CISO mediante Inteligencia Artificial.”</i>", st_body_bold)],
        [Paragraph("4 PILARES TECNOLÓGICOS", st_card_hdr_sky)],
        [Paragraph(
            "• <b>1. IPS Netmap:</b> pfSense 2.9.0 & Suricata 7.x Inline Hardware Drop.<br/>"
            "• <b>2. DMZ & HAProxy:</b> SSL Offloading y Stick-Tables anti-fuzzing L7.<br/>"
            "• <b>3. Motor KRONOS:</b> Parser AST en Python 3.12 y pfctl -k.<br/>"
            "• <b>4. Voice SOAR:</b> Asterisk 20 PBX Docker y Gemini Live Flash 3.1.",
            st_body
        )]
    ]
    t_d_left = Table(desc_left_data, colWidths=[400])
    t_d_left.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,2), (-1,2), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,1), CARD_BG),
        ('BACKGROUND', (0,3), (-1,3), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, CYAN_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))

    t_d_right_data = [
        [Paragraph("TOPOLOGÍA DE ARQUITECTURA GLOBAL KRONOS SENTINEL", st_card_hdr_green)],
        [arch_flowable]
    ]
    t_d_right = Table(t_d_right_data, colWidths=[472])
    t_d_right.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('ALIGN', (0,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,1), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))

    t_s4 = Table([[t_d_left, t_d_right]], colWidths=[404, 476])
    t_s4.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_s4)
    story.append(PageBreak())

    # SLIDE 5: VÍNCULO PERFIL DE EGRESO
    slide_header("Alineación Curricular", "Vínculo con el Perfil de Egreso (6 Competencias APT)")
    comp_data = [
        [Paragraph("COMPETENCIAS SELECCIONADAS (1 - 3)", st_card_hdr), Paragraph("COMPETENCIAS SELECCIONADAS (4 - 6)", st_card_hdr_sky)],
        [
            Paragraph(
                "• <b>Comp. 8 (Prevención y Respuesta a Riesgos):</b> Arquitectura Zero Trust en pfSense, Suricata Inline Netmap IPS y mitigación atómica en kernel con FreeBSD pfctl.<br/>"
                "• <b>Comp. 6 (Automatización y Gestión de Red):</b> Desarrollo en Python 3.12 del Motor KRONOS, parsing estructurado EVE JSON y despacho asíncrono de eventos.<br/>"
                "• <b>Comp. 5 (Unificación Voz, Datos y Video):</b> Centralita Asterisk 20 LTS en Docker, troncales PJSIP y streaming de audio RTP PCM 24kHz bidireccional.",
                st_body
            ),
            Paragraph(
                "• <b>Comp. 4 (Control y Operación de Redes):</b> Segmentación L2/L3 en 4 VLANs 802.1Q (Corp 10, DMZ 20, VoIP 30, Mgmt 99), direccionamiento CIDR y DHCP relay.<br/>"
                "• <b>Comp. 3 (Adaptación de Tecnologías de Punta):</b> Integración de IA Generativa Multimodal (Gemini Live Flash 3.1) y malla Zero Trust con Tailscale Subnet Router.<br/>"
                "• <b>Comp. 7 (Gestión de Vulnerabilidades):</b> Mitigación de vectores web (SQLi, RCE), laboratorio DVWA y Stick-Tables dinámicas en HAProxy.",
                st_body
            )
        ]
    ]
    t_s5 = Table(comp_data, colWidths=[436, 444])
    t_s5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_s5)
    story.append(PageBreak())

    # SLIDE 6: INTERESES PROFESIONALES
    slide_header("Proyección Laboral", "Relación con Intereses y Proyección Profesional")
    prof_data = [
        [Paragraph("ESPECIALIZACIÓN EN CIBERSEGURIDAD & SECOPS", st_card_hdr), Paragraph("APORTE AL DESARROLLO DEL EQUIPO DUOC UC", st_card_hdr_sky)],
        [
            Paragraph(
                "• <b>Pasión por la Ciberdefensa Activa:</b> Consolidación de aprendizajes en Hardening Perimetral, Prevención de Intrusiones (IPS) y Sistemas Autónomos SOAR.<br/>"
                "• <b>Trayectoria Práctica y Laboratorios:</b> Experiencia en Home Labs bare-metal con Proxmox VE, administración de pfSense en producción y liderazgo en CTFs con el equipo DevSec.<br/>"
                "• <b>Proyección a 5 Años:</b> Desempeñarse como Ingeniero de Ciberseguridad / Arquitecto SecOps liderando equipos de respuesta ante amenazas APT.",
                st_body
            ),
            Paragraph(
                "• <b>Soluciones Enterprise a Costo $0 CLP:</b> Capacidad de desplegar seguridad de nivel corporativo 100% con tecnologías Open Source sin licenciamiento comercial.<br/>"
                "• <b>Interoperabilidad Multi-Disciplina:</b> Integración real entre Networking L2/L3, Telefonía VoIP SIP, Hardening de Sistemas Unix (FreeBSD) e Inteligencia Artificial.<br/>"
                "• <b>Alineación con Estándares Internacionales:</b> Preparación directa para certificaciones Cisco CCNA (200-301), CompTIA Security+ y marco Zero Trust NIST SP 800-207.",
                st_body
            )
        ]
    ]
    t_s6 = Table(prof_data, colWidths=[436, 444])
    t_s6.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_s6)
    story.append(PageBreak())

    # SLIDE 7: FACTIBILIDAD Y RIESGOS
    slide_header("Viabilidad & Mitigaciones", "Factibilidad Técnica, Recursos y Gestión de Riesgos")
    fact_data = [
        [Paragraph("FACTIBILIDAD Y RECURSOS ($0 CLP)", st_card_hdr_green), Paragraph("MATRIZ DE RIESGOS Y MITIGACIÓN TÉCNICA", st_card_hdr_amber)],
        [
            Paragraph(
                "• <b>Temporalidad Académica:</b> 18 semanas semestrales (72h de taller presencial + 144h de laboratorio autónomo).<br/>"
                "• <b>Materiales 100% Open Source ($0 CLP):</b> FreeBSD 14, pfSense CE 2.9.0, Suricata 7.x, HAProxy, Asterisk 20, Docker y Python 3.12.<br/>"
                "• <b>Capas Gratuitas Comunitarias:</b> Google AI Studio (Gemini Live Free Tier) y MaxMind GeoLite2.<br/>"
                "• <b>Infraestructura:</b> Laboratorios de redes Duoc UC y virtualización en Proxmox VE / VMware.",
                st_body
            ),
            Paragraph(
                "• <b>Riesgo 1 (Bloqueo de Puertos / CGNAT):</b><br/>"
                "  <i>Mitigación:</i> Despliegue de Tailscale Subnet Router publicando la VLAN VoIP mediante WireGuard Zero Trust sin requerir IP pública.<br/>"
                "• <b>Riesgo 2 (Falsos Positivos Saturando Llamadas):</b><br/>"
                "  <i>Mitigación:</i> Filtro heurístico AST en Python 3.12 que exige confirmación atómica en tabla &lt;snort2c&gt;.<br/>"
                "• <b>Riesgo 3 (Latencia de Voz en IA):</b><br/>"
                "  <i>Mitigación:</i> Streaming directo por WebSocket PCM 24kHz con latencia &lt;400ms.",
                st_body
            )
        ]
    ]
    t_s7 = Table(fact_data, colWidths=[436, 444])
    t_s7.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_s7)
    story.append(PageBreak())

    # SLIDE 8: OBJETIVOS GENERAL Y ESPECÍFICOS
    slide_header("Metas Técnicas de Ingeniería", "Objetivos General y Específicos del Proyecto")
    obj_table_data = [
        [Paragraph("OBJETIVO GENERAL DEL PROYECTO", st_card_hdr), Paragraph("OBJETIVOS ESPECÍFICOS (1 - 4)", st_card_hdr_sky), Paragraph("OBJETIVOS ESPECÍFICOS (5 - 8)", st_card_hdr_green)],
        [
            Paragraph("Diseñar, implementar y validar una arquitectura SOAR autónoma de costo cero ($0 CLP) denominada <b>KRONOS SENTINEL</b>, integrando prevención IPS en kernel, supresión heurística de falsos positivos y notificación interactiva por voz en tiempo real con Inteligencia Artificial hacia el CISO.", st_body_bold),
            Paragraph(
                "1. <b>Segmentación L2/L3:</b> 4 VLANs 802.1Q en pfSense.<br/>"
                "2. <b>Prevención Netmap:</b> Suricata 7.x Inline Hardware Drop.<br/>"
                "3. <b>Capa DMZ Segura:</b> HAProxy 2.8+ SSL & Stick-Tables.<br/>"
                "4. <b>Motor KRONOS:</b> Parser AST en Python 3.12 anti-ruido.",
                st_body
            ),
            Paragraph(
                "5. <b>Kernel FreeBSD:</b> pfctl -k (Kill States) & &lt;snort2c&gt;.<br/>"
                "6. <b>Telefonía VoIP:</b> Asterisk 20 LTS & Auto-Dialer AMI.<br/>"
                "7. <b>Agente IA Voz:</b> Cliente WebSocket Gemini Live PCM.<br/>"
                "8. <b>Validación QA:</b> Pruebas de penetración y latencia &lt;1.5s.",
                st_body
            )
        ]
    ]
    t_s8 = Table(obj_table_data, colWidths=[300, 290, 290])
    t_s8.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_s8)
    story.append(PageBreak())

    # SLIDE 9: METODOLOGÍA Y ROLES
    slide_header("Organización y Metodología", "Metodología de Trabajo y Distribución de Roles")
    fases_work_data = [
        [
            Paragraph("FASE 1: DISEÑO & TOPOLOGÍA", st_card_hdr),
            Paragraph("FASE 2: PERÍMETRO & DMZ", st_card_hdr_sky),
            Paragraph("FASE 3: KRONOS & VOZ IA", st_card_hdr_amber),
            Paragraph("FASE 4: INTEGRACIÓN & QA", st_card_hdr_green)
        ],
        [
            Paragraph("Modelamiento IP, troncal VLAN 802.1Q y tuning de pfSense.", st_muted),
            Paragraph("Suricata Netmap Inline IPS, pfBlockerNG y HAProxy SSL.", st_muted),
            Paragraph("Motor Python 3.12 AST, pfctl wrappers y Gemini Live.", st_muted),
            Paragraph("Simulación SQLi en vivo, métricas &lt;1.5s y documentación.", st_muted)
        ]
    ]
    t_s9_fases = Table(fases_work_data, colWidths=[220, 220, 220, 220])
    t_s9_fases.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_s9_fases)
    story.append(Spacer(1, 6))

    roles_table_data = [
        [
            Paragraph("BRUNO URREA ORTIZ", st_card_hdr),
            Paragraph("FREDDY VÁSQUEZ CORTÉS", st_card_hdr_sky),
            Paragraph("CRISTÓBAL QUEZADA", st_card_hdr_amber),
            Paragraph("KEVIN RETAMALES", st_card_hdr_green)
        ],
        [
            Paragraph("<b>Rol:</b> Líder Ciberseguridad<br/>• Arquitectura Global<br/>• Motor KRONOS AST<br/>• pfctl wrappers kernel<br/>• WebSocket Gemini Live", st_body),
            Paragraph("<b>Rol:</b> Routing & VoIP<br/>• Troncal 802.1Q L2/L3<br/>• Asterisk 20 Docker<br/>• Auto-dialer AMI SIP<br/>• Malla Tailscale Mesh", st_body),
            Paragraph("<b>Rol:</b> Servicios Web DMZ<br/>• HAProxy 2.8+ SSL<br/>• Stick-Tables Anti-Fuzz<br/>• Contenedor DVWA<br/>• Hardening HTTP/TLS", st_body),
            Paragraph("<b>Rol:</b> Hardening & QA<br/>• pfSense Zero Trust<br/>• pfBlockerNG GeoIP<br/>• Listas FireHOL<br/>• Matrices de prueba QA", st_body)
        ]
    ]
    t_s9_roles = Table(roles_table_data, colWidths=[220, 220, 220, 220])
    t_s9_roles.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_s9_roles)
    story.append(PageBreak())

    # SLIDE 10: EVIDENCIAS & DIAGRAMA VOICE SOAR
    slide_header("Entregables Formales", "Evidencias Comprometidas & Pipeline de Orquestación por Voz")
    voice_img_path = "assets/voice_soar_flow.png"
    voice_flowable = Image(voice_img_path, width=440, height=250) if os.path.exists(voice_img_path) else Paragraph("<i>[voice_soar_flow.png]</i>", st_muted)

    evi_left_data = [
        [Paragraph("EVIDENCIAS DE AVANCE (FASE 1 & 2)", st_card_hdr)],
        [Paragraph(
            "• <b>[F1] Informe de Definición y Topología:</b> Documento con diseño L2/L3, direccionamiento y justificación metodológica.<br/>"
            "• <b>[F2] Repositorio Git e IaC:</b> Código Python del motor, Dockerfiles Asterisk/DVWA y XML pfSense.<br/>"
            "• <b>[F2] Manuales Técnicos PDF:</b> Manual pfSense 2.9.0 y Tutorial Paso a Paso con WebGUI mockups.",
            st_body
        )],
        [Paragraph("EVIDENCIAS FINALES & DEMO EN VIVO (FASE 3)", st_card_hdr_green)],
        [Paragraph(
            "• <b>[F3] Demostración en Vivo:</b> Ataque SQLi ➔ Bloqueo Netmap ➔ pfctl Kill States ➔ Llamada por voz Gemini Live.<br/>"
            "• <b>[F3] Registros Forenses & QA:</b> EVE JSON, tablas snort2c y telemetría (&lt;1.5s).",
            st_body
        )]
    ]
    t_e_left = Table(evi_left_data, colWidths=[430])
    t_e_left.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,2), (-1,2), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,1), CARD_BG),
        ('BACKGROUND', (0,3), (-1,3), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))

    t_e_right_data = [
        [Paragraph("PIPELINE DE NOTIFICACIÓN & RESPUESTA POR VOZ (IA SOAR)", st_card_hdr_sky)],
        [voice_flowable]
    ]
    t_e_right = Table(t_e_right_data, colWidths=[442])
    t_e_right.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('ALIGN', (0,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,1), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))

    t_s10 = Table([[t_e_left, t_e_right]], colWidths=[436, 444])
    t_s10.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_s10)
    story.append(PageBreak())

    # SLIDE 11: PLAN DE TRABAJO Y CARTA GANTT
    slide_header("Cronograma Temporal", "Plan de Trabajo y Carta Gantt (18 Semanas)")
    gantt_img_path = "assets/gantt_fase1_timeline.png"
    gantt_flowable = Image(gantt_img_path, width=880, height=240) if os.path.exists(gantt_img_path) else Paragraph("<i>[gantt_fase1_timeline.png]</i>", st_muted)

    gantt_header_data = [
        [Paragraph("MATRIZ CRONOLÓGICA DE 18 SEMANAS & HITOS APT122 (ROADMAP)", st_card_hdr)],
        [gantt_flowable]
    ]
    t_g_hdr = Table(gantt_header_data, colWidths=[880])
    t_g_hdr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_LIGHT),
        ('ALIGN', (0,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,1), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_g_hdr)
    story.append(Spacer(1, 6))

    gantt_bottom_data = [
        [
            Paragraph("FASE 1 (S1-S4)", st_card_hdr),
            Paragraph("FASE 2A (S5-S10)", st_card_hdr_sky),
            Paragraph("FASE 2B (S11-S15)", st_card_hdr_amber),
            Paragraph("FASE 3 (S16-S18)", st_card_hdr_green)
        ],
        [
            Paragraph("Setup pfSense & VLANs 802.1Q (Corp 10, DMZ 20, VoIP 30). Informe EA1.", st_muted),
            Paragraph("Suricata Netmap Inline IPS, GeoIP pfBlockerNG y HAProxy SSL DMZ.", st_muted),
            Paragraph("Motor KRONOS AST, Asterisk PBX, Gemini Live Voice y Tailscale Mesh.", st_muted),
            Paragraph("Pruebas QA &lt;1.5s, Manuales PDF y Defensa Portafolio APT122.", st_muted)
        ]
    ]
    t_g_bot = Table(gantt_bottom_data, colWidths=[220, 220, 220, 220])
    t_g_bot.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_g_bot)
    story.append(PageBreak())

    # SLIDE 12: CIERRE & CONCLUSIÓN
    slide_header("Conclusión y Ronda de Consultas", "Cierre, Próximos Pasos (Fase 2) y Preguntas")
    
    shield_close_path = "assets/sentinel_shield_logo.png"
    shield_close_img = Image(shield_close_path, width=70, height=70) if os.path.exists(shield_close_path) else Paragraph("<b>[SHIELD]</b>", st_card_hdr)

    cierre_table_data = [
        [Paragraph("PRÓXIMOS PASOS HACIA FASE 2", st_card_hdr), Paragraph("ESPACIO DE PREGUNTAS Y CONCLUSIÓN", st_card_hdr_green)],
        [
            Paragraph(
                "1. <b>Despliegue Suricata Inline Netmap:</b><br/>"
                "• Configuración de dropsid.conf para hardware drop inmediato.<br/><br/>"
                "2. <b>Hardening de HAProxy en DMZ:</b><br/>"
                "• Parametrización de Stick-Tables dinámicas anti-fuzzing L7.<br/><br/>"
                "3. <b>Desarrollo Motor KRONOS (Python 3.12):</b><br/>"
                "• Implementación de AST parser heurístico y llamadas pfctl -k.<br/><br/>"
                "4. <b>Pruebas Asterisk & Gemini Live:</b><br/>"
                "• Validación de streaming bidireccional PCM 24kHz a softphone.",
                st_body
            ),
            Table([
                [shield_close_img],
                [Paragraph("<b>KRONOS SENTINEL</b><br/><font color='#00F0FF'>Autonomous AI-IPS & Voice SOAR Architecture</font>", st_center)],
                [Paragraph("<i>“Innovación en Ciberdefensa: Desacoplando la contención atómica en kernel de la comunicación estratégica de voz en tiempo real.”</i>", st_center)],
                [Paragraph("<b>¡Muchas gracias por su atención!</b><br/>Quedamos a disposición de la Comisión Evaluadora de Duoc UC para responder sus consultas y requerimientos.", st_center)]
            ], colWidths=[420])
        ]
    ]
    t_s12 = Table(cierre_table_data, colWidths=[436, 444])
    t_s12.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CARD_HDR_BG),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_C),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_C),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_s12)

    doc.build(story, canvasmaker=LoFiSlideCanvas)
    print(f"[OK] Landscape 16:9 Lo-Fi Purple PDF Slides generated: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf_slides()
