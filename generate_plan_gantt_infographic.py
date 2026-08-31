#!/usr/bin/env python3
"""
Generador del Infográfico Maestro: Plan de Trabajo (Sección 7) y Carta Gantt (Sección 8)
Para visualización inmediata en README.md y documentación técnica.
"""

import os
import subprocess
import tempfile

SVG_PATH = "assets/plan_trabajo_gantt_fase1_infographic.svg"
PNG_PATH = "assets/plan_trabajo_gantt_fase1_infographic.png"

def build_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2400 1620" width="100%" height="100%">
  <defs>
    <!-- Background Gradient -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06030F"/>
      <stop offset="40%" stop-color="#0F0924"/>
      <stop offset="75%" stop-color="#180C38"/>
      <stop offset="100%" stop-color="#080314"/>
    </linearGradient>

    <!-- Card Background Gradient -->
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#180E38" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#0E0824" stop-opacity="0.95"/>
    </linearGradient>

    <!-- Phase Gradients for Gantt -->
    <linearGradient id="f1Grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#8B5CF6"/>
      <stop offset="100%" stop-color="#06B6D4"/>
    </linearGradient>

    <linearGradient id="f2Grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3B82F6"/>
      <stop offset="100%" stop-color="#8B5CF6"/>
    </linearGradient>

    <linearGradient id="f3Grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#10B981"/>
      <stop offset="100%" stop-color="#06B6D4"/>
    </linearGradient>

    <linearGradient id="amberGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#F59E0B"/>
      <stop offset="100%" stop-color="#EC4899"/>
    </linearGradient>

    <!-- Filters for subtle glow -->
    <filter id="glowCyan" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    
    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
  </defs>

  <style>
    .title { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-weight: 800; fill: #FFFFFF; }
    .subtitle { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-weight: 600; fill: #A78BFA; }
    .header-tag { font-family: 'Consolas', 'Courier New', monospace; font-size: 18px; font-weight: bold; }
    .sec-title { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 26px; font-weight: 700; fill: #00F5FF; }
    .card-title { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 20px; font-weight: 700; fill: #F8FAFC; }
    .card-meta { font-family: 'Consolas', monospace; font-size: 15px; font-weight: 600; }
    .card-body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 14.5px; fill: #CBD5E1; }
    .gantt-text { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 15px; font-weight: 600; fill: #E2E8F0; }
    .gantt-week { font-family: 'Consolas', monospace; font-size: 14px; font-weight: bold; fill: #94A3B8; text-anchor: middle; }
    .gantt-bar-text { font-family: 'Consolas', monospace; font-size: 13.5px; font-weight: bold; fill: #FFFFFF; }
  </style>

  <!-- Background Canvas -->
  <rect width="2400" height="1620" fill="url(#bgGrad)"/>

  <!-- Subtle Perspective Grid -->
  <g opacity="0.08" stroke="#8B5CF6" stroke-width="1">
    <line x1="0" y1="120" x2="2400" y2="120"/>
    <line x1="0" y1="240" x2="2400" y2="240"/>
    <line x1="0" y1="360" x2="2400" y2="360"/>
    <line x1="0" y1="480" x2="2400" y2="480"/>
    <line x1="0" y1="600" x2="2400" y2="600"/>
    <line x1="0" y1="720" x2="2400" y2="720"/>
    <line x1="0" y1="840" x2="2400" y2="840"/>
    <line x1="0" y1="960" x2="2400" y2="960"/>
    <line x1="0" y1="1080" x2="2400" y2="1080"/>
    <line x1="0" y1="1200" x2="2400" y2="1200"/>
    <line x1="0" y1="1320" x2="2400" y2="1320"/>
    <line x1="0" y1="1440" x2="2400" y2="1440"/>
  </g>

  <!-- ========================================================================= -->
  <!-- 1. HEADER HERO SECTION -->
  <!-- ========================================================================= -->
  <g transform="translate(80, 55)">
    <!-- Logo Badge Pill -->
    <rect x="0" y="0" width="2240" height="125" rx="16" fill="url(#cardGrad)" stroke="#4C1D95" stroke-width="1.5" filter="url(#cardShadow)"/>
    
    <text x="35" y="48" class="title" font-size="34">KRONOS SENTINEL // PLAN DE TRABAJO &amp; CARTA GANTT OFICIAL</text>
    <text x="35" y="85" class="subtitle" font-size="19">Portafolio de Título (APT122) • Duoc UC Sede San Joaquín • Estudiante: Bruno Urrea Ortiz (RUT: 21.543.637-3)</text>
    
    <!-- Badges Right -->
    <g transform="translate(1420, 32)">
      <rect x="0" y="0" width="180" height="38" rx="8" fill="#1E1242" stroke="#8B5CF6" stroke-width="1.2"/>
      <text x="90" y="24" class="header-tag" fill="#A78BFA" text-anchor="middle">18 SEMANAS</text>
      
      <rect x="200" y="0" width="180" height="38" rx="8" fill="#0A2540" stroke="#00F5FF" stroke-width="1.2"/>
      <text x="290" y="24" class="header-tag" fill="#00F5FF" text-anchor="middle">864H GRUPAL</text>

      <rect x="400" y="0" width="180" height="38" rx="8" fill="#063520" stroke="#10B981" stroke-width="1.2"/>
      <text x="490" y="24" class="header-tag" fill="#10B981" text-anchor="middle">$0 CLP LIBRE</text>

      <rect x="600" y="0" width="180" height="38" rx="8" fill="#3D1A24" stroke="#EC4899" stroke-width="1.2"/>
      <text x="690" y="24" class="header-tag" fill="#EC4899" text-anchor="middle">4 ROLES</text>
    </g>
  </g>

  <!-- ========================================================================= -->
  <!-- 2. SECCIÓN 7: PLAN DE TRABAJO (10 ACTIVIDADES CLAVE) -->
  <!-- ========================================================================= -->
  <g transform="translate(80, 215)">
    <text x="0" y="0" class="sec-title">📋 SECCIÓN 7: PLAN DE TRABAJO TÉCNICO Y GESTIÓN DE RECURSOS</text>
    <text x="750" y="-3" font-family="'Segoe UI', sans-serif" font-size="16" fill="#94A3B8">(Competencias, Responsables, Recursos y Observaciones con Factores Clave)</text>

    <!-- COLUMNA IZQUIERDA: A1 a A5 -->
    <!-- A1 -->
    <g transform="translate(0, 25)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#8B5CF6"/>
      <text x="25" y="32" class="card-title">A1. Diseño y Setup Base pfSense CE 2.9.0</text>
      <text x="490" y="32" class="card-meta" fill="#A78BFA">[Semanas 1 - 2] • Comp. 4 &amp; 8</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: B. Urrea / F. Vásquez</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Instalación en Proxmox/VMware, configuración WAN/LAN y tuning de hardware offloading para Netmap.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Docs Netgate. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Incompatibilidad TSO/LRO con Netmap; se resuelve desactivando hardware offloading.</text>
    </g>

    <!-- A2 -->
    <g transform="translate(0, 150)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#8B5CF6"/>
      <text x="25" y="32" class="card-title">A2. Segmentación de VLANs 802.1Q</text>
      <text x="420" y="32" class="card-meta" fill="#A78BFA">[Semanas 3 - 4] • Comp. 4</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Freddy Vásquez</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Creación de subredes VLAN 10 (Corp), 20 (DMZ), 30 (VoIP), 99 (Mgmt) y servidores DHCP locales.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Soporte nativo 802.1Q. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Filtrado inter-VLAN; se soluciona con reglas Zero Trust estrictas por interfaz.</text>
    </g>

    <!-- A3 -->
    <g transform="translate(0, 275)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#3B82F6"/>
      <text x="25" y="32" class="card-title">A3. Despliegue de Suricata 7.x Inline Netmap IPS</text>
      <text x="500" y="32" class="card-meta" fill="#38BDF8">[Semanas 5 - 6] • Comp. 7 &amp; 8</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: B. Urrea / K. Retamales</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Activación de modo Inline Netmap, reglas ET Open y configuración de políticas automáticas dropsid.conf.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Descarte en hardware ring-buffer. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Falsos positivos de firmas; se ajustan SIDs selectivos.</text>
    </g>

    <!-- A4 -->
    <g transform="translate(0, 400)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#3B82F6"/>
      <text x="25" y="32" class="card-title">A4. Hardening GeoIP con pfBlockerNG-devel</text>
      <text x="475" y="32" class="card-meta" fill="#38BDF8">[Semanas 7 - 8] • Comp. 7 &amp; 8</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Kevin Retamales</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Integración de MaxMind GeoLite2 Free, listas Top Spammers y feeds FireHOL L1 / Spamhaus DROP.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Feeds globales actualizados. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Consumo de RAM; se optimiza el límite de tablas en pfSense.</text>
    </g>

    <!-- A5 -->
    <g transform="translate(0, 525)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#3B82F6"/>
      <text x="25" y="32" class="card-title">A5. Proxy Inverso HAProxy 2.8+ SSL &amp; DMZ DVWA</text>
      <text x="500" y="32" class="card-meta" fill="#38BDF8">[Semanas 9 - 10] • Comp. 7</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Cristóbal Quezada</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Frontend HTTPS 443, SSL Offloading, Stick-Tables anti-fuzzing L7 y contenedor vulnerable de pruebas.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Stick-Tables en RAM a microsegundos. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Certificados SSL; se emite CA interna de laboratorio.</text>
    </g>

    <!-- COLUMNA DERECHA: A6 a A10 -->
    <!-- A6 -->
    <g transform="translate(1140, 25)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#F59E0B"/>
      <text x="25" y="32" class="card-title">A6. Motor de Correlación KRONOS (Python AST)</text>
      <text x="510" y="32" class="card-meta" fill="#FCD34D">[Semanas 11 - 12] • Comp. 6 &amp; 8</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Bruno Urrea</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Parser eve.json, filtro sintáctico AST (&gt;50% supresión) y wrappers pfctl (kill states y tabla snort2c).</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Librería estándar AST. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Privilegios en pfSense; se configura sudoers restringido para pfctl.</text>
    </g>

    <!-- A7 -->
    <g transform="translate(1140, 150)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#F59E0B"/>
      <text x="25" y="32" class="card-title">A7. Centralita Asterisk 20 LTS PBX &amp; Auto-Dialer AMI</text>
      <text x="530" y="32" class="card-meta" fill="#FCD34D">[Semanas 13 - 14] • Comp. 5</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Freddy Vásquez</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Docker Asterisk 20 LTS, canal PJSIP, Dialplan de emergencia y disparador AMI hacia el softphone.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Stack PJSIP moderno. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> NAT traversal; se fija directiva external_media_address.</text>
    </g>

    <!-- A8 -->
    <g transform="translate(1140, 275)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#F59E0B"/>
      <text x="25" y="32" class="card-title">A8. Integración Google Gemini Live Voice API</text>
      <text x="510" y="32" class="card-meta" fill="#FCD34D">[Semanas 14 - 15] • Comp. 3 &amp; 5</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Bruno Urrea</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Conexión WebSocket seguro, System Prompts tácticos SecOps y streaming de audio bidireccional PCM 24kHz.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Gemini Live Free Tier (&lt;400ms). <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Sincronización dúplex; se usa audio lineal nativo.</text>
    </g>

    <!-- A9 -->
    <g transform="translate(1140, 400)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#EC4899"/>
      <text x="25" y="32" class="card-title">A9. Enlace Seguro Zero Trust con Tailscale WireGuard</text>
      <text x="550" y="32" class="card-meta" fill="#F472B6">[Semana 15] • Comp. 3 &amp; 4</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Freddy Vásquez</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Publicación de la subred VoIP 192.168.30.0/24 para registro de softphones remotos sin abrir puertos.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> WireGuard evade 100% de CGNAT. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Aprobación de rutas; se autoriza en panel admin.</text>
    </g>

    <!-- A10 -->
    <g transform="translate(1140, 525)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#10B981"/>
      <text x="25" y="32" class="card-title">A10. Pruebas QA, Auditoría Forense &amp; Defensa</text>
      <text x="500" y="32" class="card-meta" fill="#6EE7B7">[Semanas 16 - 18] • Comp. 7, 8, 11</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Todo el Equipo</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Pruebas de estrés, auditoría de tiempos (&lt;1.5 s), generación de manuales PDF y preparación de defensa.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Roles delimitados y automatización. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Demo en vivo; se alistan scripts de respaldo.</text>
    </g>
  </g>

  <!-- ========================================================================= -->
  <!-- 3. SECCIÓN 8: CARTA GANTT PANORÁMICA (18 SEMANAS ACADÉMICAS) -->
  <!-- ========================================================================= -->
  <g transform="translate(80, 910)">
    <text x="0" y="0" class="sec-title">📅 SECCIÓN 8: CARTA GANTT PANORÁMICA OFICIAL (18 SEMANAS)</text>
    <text x="730" y="-3" font-family="'Segoe UI', sans-serif" font-size="16" fill="#94A3B8">(Temporalidad Académica por Fases: Fase 1 [S1-S4], Fase 2 [S5-S15], Fase 3 [S16-S18])</text>

    <!-- Gantt Table Container -->
    <g transform="translate(0, 25)">
      <rect width="2240" height="625" rx="16" fill="url(#cardGrad)" stroke="#4C1D95" stroke-width="1.5" filter="url(#cardShadow)"/>

      <!-- Gantt Headers -->
      <rect x="0" y="0" width="560" height="55" rx="16" fill="#130B29"/>
      <text x="30" y="35" font-family="'Segoe UI', sans-serif" font-size="16" font-weight="bold" fill="#F8FAFC">ACTIVIDAD / RESPONSABLE</text>

      <!-- Fases Superiores -->
      <!-- Fase 1 Header (S1-S4: width 360) -->
      <rect x="560" y="0" width="373" height="28" fill="#1C0F3F" stroke="#372068" stroke-width="0.8"/>
      <text x="746" y="20" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold" fill="#00F5FF" text-anchor="middle">FASE 1: DEFINICIÓN &amp; DISEÑO (S1 - S4)</text>

      <!-- Fase 2 Header (S5-S15: width 1026) -->
      <rect x="933" y="0" width="1027" height="28" fill="#150C38" stroke="#372068" stroke-width="0.8"/>
      <text x="1446" y="20" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold" fill="#A78BFA" text-anchor="middle">FASE 2: DESARROLLO, HARDENING &amp; DESPLIEGUE (S5 - S15)</text>

      <!-- Fase 3 Header (S16-S18: width 280) -->
      <rect x="1960" y="0" width="280" height="28" fill="#0D242E" stroke="#372068" stroke-width="0.8"/>
      <text x="2100" y="20" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold" fill="#10B981" text-anchor="middle">FASE 3: QA &amp; DEFENSA (S16 - S18)</text>

      <!-- Week Columns (S1 a S18) -->
      <!-- Total width for 18 weeks = 1680 px -> ~93.33 px per week -->
      <!-- S1 to S18 loop -->
    </g>
  </g>
</svg>"""

    # We will generate the complete SVG programmatically with accurate bar coordinates
    return generate_complete_svg()

def generate_complete_svg():
    # Geometry calculations for the Gantt Grid
    origin_x = 560
    week_w = 1680.0 / 18.0  # 93.333 px per week
    
    rows_data = [
        ("A1. Setup Base pfSense & Netmap Tuning", "Bruno Urrea / Freddy Vásquez", [1, 2], "#8B5CF6", "#06B6D4"),
        ("A2. Segmentación de VLANs 802.1Q", "Freddy Vásquez", [3, 4], "#8B5CF6", "#06B6D4"),
        ("A3. Suricata 7.x Inline Netmap IPS", "Bruno Urrea / Kevin Retamales", [5, 6], "#3B82F6", "#8B5CF6"),
        ("A4. Hardening GeoIP pfBlockerNG-devel", "Kevin Retamales", [7, 8], "#3B82F6", "#8B5CF6"),
        ("A5. Proxy HAProxy 2.8+ SSL & DMZ DVWA", "Cristóbal Quezada", [9, 10], "#3B82F6", "#8B5CF6"),
        ("A6. Motor Correlación KRONOS (Python AST)", "Bruno Urrea", [11, 12], "#F59E0B", "#EC4899"),
        ("A7. Centralita Asterisk 20 LTS PBX & AMI", "Freddy Vásquez", [13, 14], "#F59E0B", "#EC4899"),
        ("A8. Integración Google Gemini Live API", "Bruno Urrea", [14, 15], "#F59E0B", "#EC4899"),
        ("A9. Malla Zero Trust Tailscale WireGuard", "Freddy Vásquez", [15], "#EC4899", "#8B5CF6"),
        ("A10. Pruebas QA, Auditoría & Defensa", "Todo el Equipo", [16, 17, 18], "#10B981", "#06B6D4")
    ]

    # Build week column headers
    week_headers_svg = ""
    for w in range(1, 19):
        x = origin_x + (w - 1) * week_w
        week_headers_svg += f"""
        <rect x="{x}" y="28" width="{week_w}" height="27" fill="#0D0721" stroke="#25144A" stroke-width="0.8"/>
        <text x="{x + week_w/2}" y="47" class="gantt-week">S{w}</text>
        """

    # Build rows and timeline bars
    row_height = 54
    rows_svg = ""
    for idx, (title, resp, weeks, c1, c2) in enumerate(rows_data):
        y = 55 + idx * row_height
        bg_fill = "#130A2E" if idx % 2 == 0 else "#0F0724"
        
        # Row label
        rows_svg += f"""
        <g transform="translate(0, {y})">
          <rect width="2240" height="{row_height}" fill="{bg_fill}" stroke="#231347" stroke-width="0.5"/>
          <text x="30" y="24" class="gantt-text" font-weight="700">{title}</text>
          <text x="30" y="44" font-family="'Consolas', monospace" font-size="13" fill="#A78BFA">👤 {resp}</text>
        </g>
        """

        # Bar coordinates
        start_w = weeks[0]
        num_w = len(weeks)
        bar_x = origin_x + (start_w - 1) * week_w + 6
        bar_w = num_w * week_w - 12
        bar_y = y + 10
        bar_h = row_height - 20

        # Unique gradient id
        grad_id = f"barGrad_{idx}"
        rows_svg += f"""
        <defs>
          <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="{c1}"/>
            <stop offset="100%" stop-color="{c2}"/>
          </linearGradient>
        </defs>
        <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="8" fill="url(#{grad_id})" stroke="#FFFFFF" stroke-width="0.8" opacity="0.95" filter="url(#cardShadow)"/>
        <text x="{bar_x + bar_w/2}" y="{bar_y + 22}" class="gantt-bar-text" text-anchor="middle">S{start_w} - S{weeks[-1]} ({num_w} Sem.)</text>
        """

    complete_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2400 1620" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06030F"/>
      <stop offset="40%" stop-color="#0F0924"/>
      <stop offset="75%" stop-color="#180C38"/>
      <stop offset="100%" stop-color="#080314"/>
    </linearGradient>

    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#180E38" stop-opacity="0.90"/>
      <stop offset="100%" stop-color="#0E0824" stop-opacity="0.96"/>
    </linearGradient>

    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
  </defs>

  <style>
    .title {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-weight: 800; fill: #FFFFFF; }}
    .subtitle {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-weight: 600; fill: #A78BFA; }}
    .header-tag {{ font-family: 'Consolas', 'Courier New', monospace; font-size: 17px; font-weight: bold; }}
    .sec-title {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 26px; font-weight: 700; fill: #00F5FF; }}
    .card-title {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 20px; font-weight: 700; fill: #F8FAFC; }}
    .card-meta {{ font-family: 'Consolas', monospace; font-size: 15px; font-weight: 600; }}
    .card-body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 14.5px; fill: #CBD5E1; }}
    .gantt-text {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 15.5px; font-weight: 600; fill: #E2E8F0; }}
    .gantt-week {{ font-family: 'Consolas', monospace; font-size: 14px; font-weight: bold; fill: #94A3B8; text-anchor: middle; }}
    .gantt-bar-text {{ font-family: 'Consolas', monospace; font-size: 13.5px; font-weight: bold; fill: #FFFFFF; }}
  </style>

  <!-- Background Canvas -->
  <rect width="2400" height="1620" fill="url(#bgGrad)"/>

  <!-- Perspective Ambient Grid -->
  <g opacity="0.08" stroke="#8B5CF6" stroke-width="1">
    <line x1="0" y1="120" x2="2400" y2="120"/>
    <line x1="0" y1="240" x2="2400" y2="240"/>
    <line x1="0" y1="360" x2="2400" y2="360"/>
    <line x1="0" y1="480" x2="2400" y2="480"/>
    <line x1="0" y1="600" x2="2400" y2="600"/>
    <line x1="0" y1="720" x2="2400" y2="720"/>
    <line x1="0" y1="840" x2="2400" y2="840"/>
    <line x1="0" y1="960" x2="2400" y2="960"/>
    <line x1="0" y1="1080" x2="2400" y2="1080"/>
    <line x1="0" y1="1200" x2="2400" y2="1200"/>
    <line x1="0" y1="1320" x2="2400" y2="1320"/>
    <line x1="0" y1="1440" x2="2400" y2="1440"/>
  </g>

  <!-- ========================================================================= -->
  <!-- 1. HEADER HERO SECTION -->
  <!-- ========================================================================= -->
  <g transform="translate(80, 50)">
    <rect x="0" y="0" width="2240" height="120" rx="16" fill="url(#cardGrad)" stroke="#4C1D95" stroke-width="1.5" filter="url(#cardShadow)"/>
    <text x="35" y="48" class="title" font-size="34">KRONOS SENTINEL // PLAN DE TRABAJO &amp; CARTA GANTT OFICIAL</text>
    <text x="35" y="85" class="subtitle" font-size="19">Portafolio de Título (APT122) • Duoc UC Sede San Joaquín • Estudiante: Bruno Urrea Ortiz (RUT: 21.543.637-3)</text>
    
    <g transform="translate(1440, 42)">
      <rect x="0" y="0" width="170" height="38" rx="8" fill="#1E1242" stroke="#8B5CF6" stroke-width="1.2"/>
      <text x="85" y="24" class="header-tag" fill="#A78BFA" text-anchor="middle">18 SEMANAS</text>
      
      <rect x="190" y="0" width="170" height="38" rx="8" fill="#0A2540" stroke="#00F5FF" stroke-width="1.2"/>
      <text x="275" y="24" class="header-tag" fill="#00F5FF" text-anchor="middle">864H GRUPAL</text>

      <rect x="380" y="0" width="170" height="38" rx="8" fill="#063520" stroke="#10B981" stroke-width="1.2"/>
      <text x="465" y="24" class="header-tag" fill="#10B981" text-anchor="middle">$0 CLP LIBRE</text>

      <rect x="570" y="0" width="170" height="38" rx="8" fill="#3D1A24" stroke="#EC4899" stroke-width="1.2"/>
      <text x="655" y="24" class="header-tag" fill="#EC4899" text-anchor="middle">4 ROLES</text>
    </g>
  </g>

  <!-- ========================================================================= -->
  <!-- 2. SECCIÓN 7: PLAN DE TRABAJO (10 ACTIVIDADES CLAVE) -->
  <!-- ========================================================================= -->
  <g transform="translate(80, 205)">
    <text x="0" y="0" class="sec-title">📋 SECCIÓN 7: PLAN DE TRABAJO TÉCNICO Y GESTIÓN DE RECURSOS</text>
    <text x="750" y="-3" font-family="'Segoe UI', sans-serif" font-size="16" fill="#94A3B8">(Competencias, Responsables, Recursos y Observaciones con Factores Clave)</text>

    <!-- COLUMNA IZQUIERDA: A1 a A5 -->
    <!-- A1 -->
    <g transform="translate(0, 20)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#8B5CF6"/>
      <text x="25" y="32" class="card-title">A1. Diseño y Setup Base pfSense CE 2.9.0</text>
      <text x="490" y="32" class="card-meta" fill="#A78BFA">[Semanas 1 - 2] • Comp. 4 &amp; 8</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: B. Urrea / F. Vásquez</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Instalación en Proxmox/VMware, configuración WAN/LAN y tuning de hardware offloading para Netmap.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Docs Netgate. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Incompatibilidad TSO/LRO con Netmap; se resuelve desactivando hardware offloading.</text>
    </g>

    <!-- A2 -->
    <g transform="translate(0, 145)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#8B5CF6"/>
      <text x="25" y="32" class="card-title">A2. Segmentación de VLANs 802.1Q</text>
      <text x="420" y="32" class="card-meta" fill="#A78BFA">[Semanas 3 - 4] • Comp. 4</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Freddy Vásquez</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Creación de subredes VLAN 10 (Corp), 20 (DMZ), 30 (VoIP), 99 (Mgmt) y servidores DHCP locales.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Soporte nativo 802.1Q. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Filtrado inter-VLAN; se soluciona con reglas Zero Trust estrictas por interfaz.</text>
    </g>

    <!-- A3 -->
    <g transform="translate(0, 270)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#3B82F6"/>
      <text x="25" y="32" class="card-title">A3. Despliegue de Suricata 7.x Inline Netmap IPS</text>
      <text x="500" y="32" class="card-meta" fill="#38BDF8">[Semanas 5 - 6] • Comp. 7 &amp; 8</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: B. Urrea / K. Retamales</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Activación de modo Inline Netmap, reglas ET Open y configuración de políticas automáticas dropsid.conf.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Descarte en hardware ring-buffer. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Falsos positivos de firmas; se ajustan SIDs selectivos.</text>
    </g>

    <!-- A4 -->
    <g transform="translate(0, 395)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#3B82F6"/>
      <text x="25" y="32" class="card-title">A4. Hardening GeoIP con pfBlockerNG-devel</text>
      <text x="475" y="32" class="card-meta" fill="#38BDF8">[Semanas 7 - 8] • Comp. 7 &amp; 8</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Kevin Retamales</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Integración de MaxMind GeoLite2 Free, listas Top Spammers y feeds FireHOL L1 / Spamhaus DROP.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Feeds globales actualizados. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Consumo de RAM; se optimiza el límite de tablas en pfSense.</text>
    </g>

    <!-- A5 -->
    <g transform="translate(0, 520)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#3B82F6"/>
      <text x="25" y="32" class="card-title">A5. Proxy Inverso HAProxy 2.8+ SSL &amp; DMZ DVWA</text>
      <text x="500" y="32" class="card-meta" fill="#38BDF8">[Semanas 9 - 10] • Comp. 7</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Cristóbal Quezada</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Frontend HTTPS 443, SSL Offloading, Stick-Tables anti-fuzzing L7 y contenedor vulnerable de pruebas.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Stick-Tables en RAM a microsegundos. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Certificados SSL; se emite CA interna de laboratorio.</text>
    </g>

    <!-- COLUMNA DERECHA: A6 a A10 -->
    <!-- A6 -->
    <g transform="translate(1140, 20)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#F59E0B"/>
      <text x="25" y="32" class="card-title">A6. Motor de Correlación KRONOS (Python AST)</text>
      <text x="510" y="32" class="card-meta" fill="#FCD34D">[Semanas 11 - 12] • Comp. 6 &amp; 8</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Bruno Urrea</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Parser eve.json, filtro sintáctico AST (&gt;50% supresión) y wrappers pfctl (kill states y tabla snort2c).</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Librería estándar AST. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Privilegios en pfSense; se configura sudoers restringido para pfctl.</text>
    </g>

    <!-- A7 -->
    <g transform="translate(1140, 145)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#F59E0B"/>
      <text x="25" y="32" class="card-title">A7. Centralita Asterisk 20 LTS PBX &amp; Auto-Dialer AMI</text>
      <text x="530" y="32" class="card-meta" fill="#FCD34D">[Semanas 13 - 14] • Comp. 5</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Freddy Vásquez</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Docker Asterisk 20 LTS, canal PJSIP, Dialplan de emergencia y disparador AMI hacia el softphone.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Stack PJSIP moderno. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> NAT traversal; se fija directiva external_media_address.</text>
    </g>

    <!-- A8 -->
    <g transform="translate(1140, 270)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#F59E0B"/>
      <text x="25" y="32" class="card-title">A8. Integración Google Gemini Live Voice API</text>
      <text x="510" y="32" class="card-meta" fill="#FCD34D">[Semanas 14 - 15] • Comp. 3 &amp; 5</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Bruno Urrea</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Conexión WebSocket seguro, System Prompts tácticos SecOps y streaming de audio bidireccional PCM 24kHz.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Gemini Live Free Tier (&lt;400ms). <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Sincronización dúplex; se usa audio lineal nativo.</text>
    </g>

    <!-- A9 -->
    <g transform="translate(1140, 395)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#EC4899"/>
      <text x="25" y="32" class="card-title">A9. Enlace Seguro Zero Trust con Tailscale WireGuard</text>
      <text x="550" y="32" class="card-meta" fill="#F472B6">[Semana 15] • Comp. 3 &amp; 4</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Freddy Vásquez</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Publicación de la subred VoIP 192.168.30.0/24 para registro de softphones remotos sin abrir puertos.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> WireGuard evade 100% de CGNAT. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Aprobación de rutas; se autoriza en panel admin.</text>
    </g>

    <!-- A10 -->
    <g transform="translate(1140, 520)">
      <rect width="1100" height="110" rx="12" fill="url(#cardGrad)" stroke="#372068" stroke-width="1.2" filter="url(#cardShadow)"/>
      <rect x="0" y="0" width="8" height="110" rx="4" fill="#10B981"/>
      <text x="25" y="32" class="card-title">A10. Pruebas QA, Auditoría Forense &amp; Defensa</text>
      <text x="500" y="32" class="card-meta" fill="#6EE7B7">[Semanas 16 - 18] • Comp. 7, 8, 11</text>
      <text x="830" y="32" class="card-meta" fill="#00F5FF">Resp: Todo el Equipo</text>
      <text x="25" y="62" class="card-body"><tspan fill="#F1F5F9" font-weight="600">Descripción:</tspan> Pruebas de estrés, auditoría de tiempos (&lt;1.5 s), generación de manuales PDF y preparación de defensa.</text>
      <text x="25" y="90" class="card-body"><tspan fill="#10B981" font-weight="600">✔ Facilitador:</tspan> Roles delimitados y automatización. <tspan fill="#F59E0B" font-weight="600">⚠ Obstáculo:</tspan> Demo en vivo; se alistan scripts de respaldo.</text>
    </g>
  </g>

  <!-- ========================================================================= -->
  <!-- 3. SECCIÓN 8: CARTA GANTT PANORÁMICA (18 SEMANAS ACADÉMICAS) -->
  <!-- ========================================================================= -->
  <g transform="translate(80, 905)">
    <text x="0" y="0" class="sec-title">📅 SECCIÓN 8: CARTA GANTT PANORÁMICA OFICIAL (18 SEMANAS ACADÉMICAS)</text>
    <text x="840" y="-3" font-family="'Segoe UI', sans-serif" font-size="16" fill="#94A3B8">(Temporalidad Académica: Fase 1 [S1-S4], Fase 2 [S5-S15], Fase 3 [S16-S18])</text>

    <!-- Gantt Table Container -->
    <g transform="translate(0, 20)">
      <rect width="2240" height="600" rx="16" fill="url(#cardGrad)" stroke="#4C1D95" stroke-width="1.5" filter="url(#cardShadow)"/>

      <!-- Gantt Headers -->
      <rect x="0" y="0" width="560" height="55" rx="16" fill="#130B29"/>
      <text x="30" y="35" font-family="'Segoe UI', sans-serif" font-size="16" font-weight="bold" fill="#F8FAFC">ACTIVIDAD / RESPONSABLE</text>

      <!-- Fases Superiores -->
      <!-- Fase 1 Header (S1-S4: width 373.33) -->
      <rect x="560" y="0" width="373.33" height="28" fill="#1C0F3F" stroke="#372068" stroke-width="0.8"/>
      <text x="746.66" y="19" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold" fill="#00F5FF" text-anchor="middle">FASE 1: DEFINICIÓN &amp; DISEÑO (S1 - S4)</text>

      <!-- Fase 2 Header (S5-S15: width 1026.66) -->
      <rect x="933.33" y="0" width="1026.66" height="28" fill="#150C38" stroke="#372068" stroke-width="0.8"/>
      <text x="1446.66" y="19" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold" fill="#A78BFA" text-anchor="middle">FASE 2: DESARROLLO, HARDENING &amp; DESPLIEGUE (S5 - S15)</text>

      <!-- Fase 3 Header (S16-S18: width 280) -->
      <rect x="1960" y="0" width="280" height="28" fill="#0D242E" stroke="#372068" stroke-width="0.8"/>
      <text x="2100" y="19" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold" fill="#10B981" text-anchor="middle">FASE 3: QA &amp; DEFENSA (S16 - S18)</text>

      <!-- Week Columns (S1 a S18) -->
      {week_headers_svg}

      <!-- Rows and Bars -->
      {rows_svg}
    </g>
  </g>
</svg>"""
    return complete_svg

def main():
    os.makedirs("assets", exist_ok=True)
    svg_content = build_svg()
    
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[OK] SVG generated: {SVG_PATH}")

    # Convert to 4K crystalline PNG using headless Edge/Chrome
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ]
    browser = next((p for p in edge_paths if os.path.exists(p)), None)
    if not browser:
        print("[WARN] No headless browser found. Only SVG saved.")
        return

    cwd = os.path.abspath(".")
    png_abs = os.path.join(cwd, PNG_PATH)
    
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 100vw; height: 100vh; overflow: hidden; background: #06030F; display: flex; align-items: center; justify-content: center; }}
svg {{ width: 100vw; height: 100vh; display: block; }}
</style>
</head><body>{svg_content}</body></html>"""

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html)
        tmp_path = tmp.name

    try:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--window-size=2400,1620",
            f"--screenshot={png_abs}",
            "file:///" + tmp_path.replace("\\", "/")
        ]
        subprocess.run(cmd, check=True)
        print(f"[OK] Rendered 4K Infographic PNG: {PNG_PATH} ({os.path.getsize(png_abs)} bytes)")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    main()
