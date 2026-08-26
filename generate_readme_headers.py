#!/usr/bin/env python3
"""
Generate Modernist Cyber-SecOps SVG Header Banners for GitHub README
Author: Bruno Urrea Ortiz (Portafolio de Título - Duoc UC)
"""

import os

headers = [
    {
        "filename": "header_01_resumen.svg",
        "num": "01",
        "title": "RESUMEN EJECUTIVO Y PROBLEMÁTICA",
        "subtitle": "CRISIS DE FALSOS POSITIVOS & NOTIFICACIÓN TÁCTICA CISO",
        "accent": "#00E5FF",
        "tag": "SOC PROBLEM STATEMENT"
    },
    {
        "filename": "header_02_arquitectura.svg",
        "num": "02",
        "title": "ARQUITECTURA GLOBAL DEL SISTEMA",
        "subtitle": "DEFENSA EN PROFUNDIDAD • INLINE NETMAP IPS • AI VOICE SOAR",
        "accent": "#00E5FF",
        "tag": "ENTERPRISE TOPOLOGY"
    },
    {
        "filename": "header_03_pfctl.svg",
        "num": "03",
        "title": "MOTOR DE CORRELACIÓN Y SUPRESIÓN PFCTL",
        "subtitle": "HEURÍSTICA AST SQLi • SUPRESIÓN >50% FALSOS POSITIVOS",
        "accent": "#38BDF8",
        "tag": "KERNEL DECISION ENGINE"
    },
    {
        "filename": "header_04_soar.svg",
        "num": "04",
        "title": "ORQUESTACIÓN SOAR Y TELEFONÍA IA",
        "subtitle": "ASTERISK PBX 20 • WEBSOCKET STREAMING GEMINI LIVE FLASH 3.1",
        "accent": "#00E5FF",
        "tag": "VOICE INCIDENT RESPONSE"
    },
    {
        "filename": "header_05_timeline.svg",
        "num": "05",
        "title": "LÍNEA DE TIEMPO DE RESPUESTA A INCIDENTES",
        "subtitle": "CRONOMETRÍA EN MILISEGUNDOS DEL WAR-ROOM SOC",
        "accent": "#F59E0B",
        "tag": "SUB-SECOND RESPONSE"
    },
    {
        "filename": "header_06_emblema.svg",
        "num": "06",
        "title": "SIMBOLISMO DEL EMBLEMA KRONOS SENTINEL",
        "subtitle": "CONVERGENCIA VECTORIAL DE IDENTIDAD PERIMETRAL",
        "accent": "#FF1E56",
        "tag": "BRAND IDENTITY"
    },
    {
        "filename": "header_07_entregables.svg",
        "num": "07",
        "title": "ESTRUCTURA DEL REPOSITORIO Y ENTREGABLES",
        "subtitle": "DOCUMENTACIÓN ACADÉMICA DUOC UC • CÓDIGO FUENTE & MANUALES",
        "accent": "#00E5FF",
        "tag": "ACADEMIC PORTAFOLIO"
    },
    {
        "filename": "header_08_despliegue.svg",
        "num": "08",
        "title": "DESPLIEGUE Y PUESTA EN MARCHA RÁPIDA",
        "subtitle": "GUÍA DE INICIALIZACIÓN DOCKER, ASTERISK & MOTOR PYTHON",
        "accent": "#10B981",
        "tag": "QUICKSTART GUIDE"
    },
    {
        "filename": "header_09_equipo.svg",
        "num": "09",
        "title": "EQUIPO DE DESARROLLO DE TITULACIÓN",
        "subtitle": "ESCUELA DE INFORMÁTICA Y TELECOMUNICACIONES — DUOC UC",
        "accent": "#38BDF8",
        "tag": "ENGINEERING TEAM"
    }
]

def generate_svg(h):
    num = h["num"]
    title = h["title"]
    subtitle = h["subtitle"]
    accent = h["accent"]
    tag = h["tag"]
    
    svg = f"""<svg width="850" height="76" viewBox="0 0 850 76" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg_grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B0F19"/>
      <stop offset="100%" stop-color="#070A11"/>
    </linearGradient>
    <linearGradient id="line_grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.8"/>
      <stop offset="70%" stop-color="#2563EB" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#1E293B" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="{accent}" flood-opacity="0.25"/>
    </filter>
  </defs>

  <!-- Background Card -->
  <rect x="1" y="1" width="848" height="74" rx="8" fill="url(#bg_grad)" stroke="#1E293B" stroke-width="1.2"/>

  <!-- Left Accent Bar -->
  <path d="M 1 9 Q 1 1 9 1 L 9 1 L 9 75 L 9 75 Q 1 75 1 67 Z" fill="{accent}"/>

  <!-- Badge Number -->
  <rect x="22" y="15" width="46" height="46" rx="6" fill="#111827" stroke="{accent}" stroke-width="1.2" filter="url(#glow)"/>
  <text x="45" y="44" fill="{accent}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif" font-weight="900" font-size="18" text-anchor="middle">{num}</text>

  <!-- Section Title -->
  <text x="82" y="36" fill="#F8FAFC" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif" font-weight="800" font-size="16" letter-spacing="0.5">{title}</text>

  <!-- Subtitle -->
  <text x="82" y="55" fill="#64748B" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif" font-weight="600" font-size="10" letter-spacing="0.8">{subtitle}</text>

  <!-- Right Tag Pill -->
  <rect x="670" y="24" width="160" height="28" rx="14" fill="#0D1527" stroke="#1E293B" stroke-width="1"/>
  <circle cx="684" cy="38" r="4" fill="{accent}"/>
  <text x="696" y="42" fill="#94A3B8" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif" font-weight="700" font-size="9.5" letter-spacing="0.6">{tag}</text>

  <!-- Bottom Accent Gradient Line -->
  <rect x="10" y="73" width="830" height="2" rx="1" fill="url(#line_grad)"/>
</svg>"""
    return svg

def main():
    out_dir = "assets/headers"
    os.makedirs(out_dir, exist_ok=True)
    for h in headers:
        svg_content = generate_svg(h)
        filepath = os.path.join(out_dir, h["filename"])
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Generated header: {filepath}")

if __name__ == "__main__":
    main()
