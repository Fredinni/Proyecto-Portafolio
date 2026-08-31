#!/usr/bin/env python3
"""
Generador Maestro de Assets Vectoriales Minimalistas (Apple Keynote / Dark SecOps)
Proyecto: KRONOS SENTINEL - Portafolio de Título (APT122)
Garantiza ratios de aspecto exactos, cero distorsión horizontal y renderizado cristalino.
"""

import os
import subprocess
import tempfile

ASSETS_DIR = "assets"

def build_svg_assets():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # 1. Gantt Timeline Widescreen (Exact 2200 x 600 -> Ratio 3.666:1)
    gantt_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2200 600" width="100%" height="100%">
  <defs>
    <linearGradient id="ganttDarkBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#121216" />
      <stop offset="100%" stop-color="#0A0A0C" />
    </linearGradient>
    <linearGradient id="barCyan" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00F0FF" /><stop offset="100%" stop-color="#0A84FF" />
    </linearGradient>
    <linearGradient id="barSky" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0A84FF" /><stop offset="100%" stop-color="#6366F1" />
    </linearGradient>
    <linearGradient id="barAmber" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FF9F0A" /><stop offset="100%" stop-color="#F59E0B" />
    </linearGradient>
    <linearGradient id="barGreen" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#30D158" /><stop offset="100%" stop-color="#10B981" />
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="2200" height="600" rx="14" fill="url(#ganttDarkBg)" stroke="#27272A" stroke-width="2" />

  <!-- Title & Subtitle -->
  <text x="50" y="55" font-family="'Segoe UI', -apple-system, sans-serif" font-size="24" font-weight="bold" fill="#F5F5F7">CRONOGRAMA DE TRABAJO &amp; HITOS (18 SEMANAS)</text>
  <text x="50" y="85" font-family="'Consolas', monospace" font-size="16" fill="#71717A">PLANIFICACIÓN SEMESTRAL ACADÉMICA APT122 // DUOC UC SAN JOAQUÍN</text>

  <!-- Week Column Headers (S1 to S18) -->
  <g transform="translate(680, 45)">
"""
    col_w = 80
    for w in range(1, 19):
        x = (w - 1) * col_w
        # Vertical grid line
        gantt_svg += f'    <line x1="{x + 40}" y1="0" x2="{x + 40}" y2="490" stroke="#1E293B" stroke-width="1.2" stroke-dasharray="4 4"/>\n'
        # Week Header Box
        gantt_svg += f'    <rect x="{x + 6}" y="10" width="68" height="34" rx="6" fill="#18181D" stroke="#27272A" stroke-width="1"/>\n'
        gantt_svg += f'    <text x="{x + 40}" y="33" font-family="Consolas, monospace" font-size="15" font-weight="bold" fill="#00F0FF" text-anchor="middle">S{w}</text>\n'

    gantt_svg += """  </g>

  <!-- Gantt Task Rows -->
  <g transform="translate(50, 120)">
    <!-- Row 1: Fase 1 -->
    <g transform="translate(0, 0)">
      <rect x="0" y="0" width="590" height="70" rx="8" fill="#16161A" stroke="#27272A" stroke-width="1" />
      <text x="20" y="32" font-family="'Segoe UI', sans-serif" font-size="18" font-weight="bold" fill="#FFFFFF">FASE 1: Definición &amp; Topología</text>
      <text x="20" y="54" font-family="Consolas, monospace" font-size="14" fill="#38BDF8">Setup pfSense 2.9.0 &amp; 4 VLANs 802.1Q (Corp, DMZ, VoIP)</text>
      <!-- Gantt Bar: Weeks 1-4 (4 cols = 320px) -->
      <rect x="636" y="12" width="308" height="46" rx="8" fill="url(#barCyan)" />
      <text x="790" y="41" font-family="'Segoe UI', sans-serif" font-size="16" font-weight="bold" fill="#000000" text-anchor="middle">S1 - S4 (Hito Fase 1)</text>
    </g>

    <!-- Row 2: Fase 2A -->
    <g transform="translate(0, 90)">
      <rect x="0" y="0" width="590" height="70" rx="8" fill="#16161A" stroke="#27272A" stroke-width="1" />
      <text x="20" y="32" font-family="'Segoe UI', sans-serif" font-size="18" font-weight="bold" fill="#FFFFFF">FASE 2A: Perímetro Netmap &amp; DMZ</text>
      <text x="20" y="54" font-family="Consolas, monospace" font-size="14" fill="#60A5FA">Suricata Inline Drop, GeoIP MaxMind &amp; HAProxy SSL</text>
      <!-- Gantt Bar: Weeks 5-10 (6 cols = 480px) -->
      <rect x="956" y="12" width="468" height="46" rx="8" fill="url(#barSky)" />
      <text x="1190" y="41" font-family="'Segoe UI', sans-serif" font-size="16" font-weight="bold" fill="#FFFFFF" text-anchor="middle">S5 - S10 (Perímetro &amp; DMZ)</text>
    </g>

    <!-- Row 3: Fase 2B -->
    <g transform="translate(0, 180)">
      <rect x="0" y="0" width="590" height="70" rx="8" fill="#16161A" stroke="#27272A" stroke-width="1" />
      <text x="20" y="32" font-family="'Segoe UI', sans-serif" font-size="18" font-weight="bold" fill="#FFFFFF">FASE 2B: Automatización SOAR &amp; Voz</text>
      <text x="20" y="54" font-family="Consolas, monospace" font-size="14" fill="#FBBF24">Motor Python AST, Asterisk AMI, Gemini Live &amp; Tailscale</text>
      <!-- Gantt Bar: Weeks 11-15 (5 cols = 400px) -->
      <rect x="1436" y="12" width="388" height="46" rx="8" fill="url(#barAmber)" />
      <text x="1630" y="41" font-family="'Segoe UI', sans-serif" font-size="16" font-weight="bold" fill="#000000" text-anchor="middle">S11 - S15 (SOAR Voz IA)</text>
    </g>

    <!-- Row 4: Fase 3 -->
    <g transform="translate(0, 270)">
      <rect x="0" y="0" width="590" height="70" rx="8" fill="#16161A" stroke="#27272A" stroke-width="1" />
      <text x="20" y="32" font-family="'Segoe UI', sans-serif" font-size="18" font-weight="bold" fill="#FFFFFF">FASE 3: QA, Validación &amp; Defensa</text>
      <text x="20" y="54" font-family="Consolas, monospace" font-size="14" fill="#34D399">Pruebas SQLi &lt;1.5s, Manuales PDF &amp; Exposición Final</text>
      <!-- Gantt Bar: Weeks 16-18 (3 cols = 240px) -->
      <rect x="1836" y="12" width="228" height="46" rx="8" fill="url(#barGreen)" />
      <text x="1950" y="41" font-family="'Segoe UI', sans-serif" font-size="16" font-weight="bold" fill="#000000" text-anchor="middle">S16 - S18 (Defensa)</text>
    </g>
  </g>

  <!-- Bottom Milestone Strip -->
  <g transform="translate(50, 500)">
    <rect width="2100" height="65" rx="10" fill="#141418" stroke="#27272A" stroke-width="1.5" />
    <circle cx="30" cy="32" r="8" fill="#00F0FF" />
    <text x="50" y="38" font-family="Consolas, monospace" font-size="16" font-weight="bold" fill="#00F0FF">HITOS ENTREGABLES:</text>
    <text x="250" y="38" font-family="'Segoe UI', sans-serif" font-size="15" fill="#E2E8F0">
      <tspan fill="#00F0FF" font-weight="bold">[S4]</tspan> Informe Definición &bull; 
      <tspan fill="#38BDF8" font-weight="bold">[S10]</tspan> Manuales Técnicos PDF &bull; 
      <tspan fill="#FF9F0A" font-weight="bold">[S15]</tspan> Demo SOAR Funcional &bull; 
      <tspan fill="#30D158" font-weight="bold">[S18]</tspan> Defensa Titulación Duoc UC
    </text>
  </g>
</svg>"""

    with open(os.path.join(ASSETS_DIR, "gantt_fase1_timeline.svg"), "w", encoding="utf-8") as f:
        f.write(gantt_svg.strip() + "\n")
    print("[OK] Generated: assets/gantt_fase1_timeline.svg (Ratio 3.66:1)")

def rasterize_all_svgs():
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ]
    browser = next((p for p in edge_paths if os.path.exists(p)), None)
    if not browser:
        print("[WARN] No headless browser found.")
        return

    cwd = os.path.abspath(".")
    
    # Lista de conversiones con sus resoluciones óptimas exactas
    targets = [
        ("assets/sentinel_shield_logo.svg", "assets/sentinel_shield_logo.png", 1600, 1600, "transparent"),
        ("assets/gantt_fase1_timeline.svg", "assets/gantt_fase1_timeline.png", 2200, 600, "#0A0A0C"),
        ("assets/architecture_diagram.svg", "assets/architecture_diagram.png", 2400, 1300, "#0A0A0C"),
        ("assets/pfctl_decision_flow.svg", "assets/pfctl_decision_flow.png", 2400, 1360, "#0A0A0C"),
        ("assets/voice_soar_flow.svg", "assets/voice_soar_flow.png", 2400, 1360, "#0A0A0C"),
    ]

    for svg_rel, png_rel, w, h, bg in targets:
        svg_abs = os.path.join(cwd, svg_rel)
        png_abs = os.path.join(cwd, png_rel)
        if not os.path.exists(svg_abs):
            continue

        with open(svg_abs, "r", encoding="utf-8") as f:
            svg_content = f.read()

        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
        <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:{bg};width:100vw;height:100vh;overflow:hidden;}} svg{{width:100vw;height:100vh;}}</style>
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
                f"--window-size={w},{h}",
                f"--screenshot={png_abs}",
                "file:///" + tmp_path.replace("\\", "/")
            ]
            subprocess.run(cmd, check=True)
            print(f"[OK] High-DPI Rasterized: {png_rel} ({w}x{h})")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    build_svg_assets()
    rasterize_all_svgs()
