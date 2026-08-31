#!/usr/bin/env python3
"""
Generador de Background Lo-Fi Púrpura con Ondas & Assets Vectoriales Transparentes
Estilo: Lo-Fi Cyberpunk / Synthwave Ambient / Midnight Purple Waves
Proyecto: KRONOS SENTINEL (APT122)
"""

import os
import subprocess
import tempfile

ASSETS_DIR = "assets"

def generate_lofi_background_svg():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # SVG Lo-Fi Waves 2560 x 1440 (Widescreen 16:9)
    lofi_bg_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2560 1440" width="100%" height="100%">
  <defs>
    <!-- Deep Space Purple Gradient Background -->
    <linearGradient id="lofiSky" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080412" />
      <stop offset="35%" stop-color="#120826" />
      <stop offset="70%" stop-color="#1C0B3B" />
      <stop offset="100%" stop-color="#0A0417" />
    </linearGradient>

    <!-- Radial Nebula Ambient Glows -->
    <radialGradient id="nebulaPurple" cx="80%" cy="20%" r="60%">
      <stop offset="0%" stop-color="#7C3AED" stop-opacity="0.25" />
      <stop offset="60%" stop-color="#5B21B6" stop-opacity="0.08" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0" />
    </radialGradient>

    <radialGradient id="nebulaCyan" cx="20%" cy="85%" r="50%">
      <stop offset="0%" stop-color="#06B6D4" stop-opacity="0.20" />
      <stop offset="50%" stop-color="#3B82F6" stop-opacity="0.06" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0" />
    </radialGradient>

    <radialGradient id="nebulaPink" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#EC4899" stop-opacity="0.12" />
      <stop offset="70%" stop-color="#8B5CF6" stop-opacity="0.04" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0" />
    </radialGradient>

    <!-- Wave Gradients -->
    <linearGradient id="waveGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#8B5CF6" stop-opacity="0.4" />
      <stop offset="50%" stop-color="#EC4899" stop-opacity="0.3" />
      <stop offset="100%" stop-color="#3B82F6" stop-opacity="0.4" />
    </linearGradient>

    <linearGradient id="waveGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#06B6D4" stop-opacity="0.3" />
      <stop offset="50%" stop-color="#8B5CF6" stop-opacity="0.4" />
      <stop offset="100%" stop-color="#D946EF" stop-opacity="0.3" />
    </linearGradient>

    <linearGradient id="waveGrad3" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3B82F6" stop-opacity="0.2" />
      <stop offset="50%" stop-color="#06B6D4" stop-opacity="0.3" />
      <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0.2" />
    </linearGradient>

    <!-- Cyber Grid Mask -->
    <pattern id="cyberGrid" width="60" height="60" patternUnits="userSpaceOnUse">
      <path d="M 60 0 L 0 0 0 60" fill="none" stroke="#A78BFA" stroke-width="0.8" stroke-opacity="0.06" />
    </pattern>

    <!-- Glow Filter -->
    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- Base Solid Background -->
  <rect width="2560" height="1440" fill="url(#lofiSky)" />

  <!-- Ambient Light Nebulas -->
  <rect width="2560" height="1440" fill="url(#nebulaPurple)" />
  <rect width="2560" height="1440" fill="url(#nebulaCyan)" />
  <rect width="2560" height="1440" fill="url(#nebulaPink)" />

  <!-- Perspective Cyber Grid in Horizon -->
  <rect width="2560" height="1440" fill="url(#cyberGrid)" />

  <!-- Lo-Fi Ambient Soundwaves / Top Ribbon -->
  <g filter="url(#softGlow)" opacity="0.6">
    <path d="M 0,180 C 400,120 700,260 1100,160 C 1500,60 1900,220 2560,130" fill="none" stroke="url(#waveGrad1)" stroke-width="2.5" />
    <path d="M 0,210 C 350,150 750,290 1200,190 C 1650,90 2050,250 2560,160" fill="none" stroke="url(#waveGrad2)" stroke-width="1.8" stroke-dasharray="6 6" />
  </g>

  <!-- Lo-Fi Bottom Horizon Waves (Cinematic Flow) -->
  <g filter="url(#softGlow)">
    <!-- Wave 1 (Deep Purple Glow) -->
    <path d="M 0,1440 L 0,1280 C 320,1210 640,1360 960,1260 C 1280,1160 1600,1320 1920,1230 C 2240,1140 2400,1270 2560,1210 L 2560,1440 Z" 
          fill="url(#waveGrad1)" opacity="0.15" />
    
    <!-- Wave Line 1 -->
    <path d="M 0,1280 C 320,1210 640,1360 960,1260 C 1280,1160 1600,1320 1920,1230 C 2240,1140 2400,1270 2560,1210" 
          fill="none" stroke="#C084FC" stroke-width="3" opacity="0.7" />

    <!-- Wave 2 (Cyan Synth Flow) -->
    <path d="M 0,1440 L 0,1340 C 380,1270 720,1400 1100,1310 C 1480,1220 1820,1380 2200,1300 C 2380,1260 2480,1320 2560,1290 L 2560,1440 Z" 
          fill="url(#waveGrad2)" opacity="0.18" />

    <!-- Wave Line 2 -->
    <path d="M 0,1340 C 380,1270 720,1400 1100,1310 C 1480,1220 1820,1380 2200,1300 C 2380,1260 2480,1320 2560,1290" 
          fill="none" stroke="#38BDF8" stroke-width="2.5" opacity="0.8" />

    <!-- Wave Line 3 (Pink Neon Pulse) -->
    <path d="M 0,1390 C 300,1330 650,1430 1020,1360 C 1390,1290 1740,1420 2100,1350 C 2350,1310 2480,1370 2560,1340" 
          fill="none" stroke="#F472B6" stroke-width="1.8" stroke-dasharray="10 6" opacity="0.75" />
  </g>

  <!-- Subtle Stardust Dots -->
  <g fill="#FFFFFF" opacity="0.35">
    <circle cx="240" cy="320" r="1.5" />
    <circle cx="580" cy="190" r="2.0" fill="#00F0FF" />
    <circle cx="920" cy="280" r="1.2" />
    <circle cx="1340" cy="140" r="2.2" fill="#E879F9" />
    <circle cx="1780" cy="260" r="1.5" />
    <circle cx="2120" cy="180" r="2.0" fill="#38BDF8" />
    <circle cx="2380" cy="340" r="1.2" />
    <circle cx="340" cy="850" r="1.8" fill="#F472B6" />
    <circle cx="820" cy="980" r="1.5" />
    <circle cx="1560" cy="920" r="2.0" fill="#00F0FF" />
    <circle cx="2240" cy="890" r="1.4" />
  </g>
</svg>"""

    bg_svg_path = os.path.join(ASSETS_DIR, "lofi_purple_waves_bg.svg")
    with open(bg_svg_path, "w", encoding="utf-8") as f:
        f.write(lofi_bg_svg.strip() + "\n")
    print(f"[OK] Created: {bg_svg_path}")

def rasterize_all():
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ]
    browser = next((p for p in edge_paths if os.path.exists(p)), None)
    if not browser:
        print("[WARN] No browser found for rasterization.")
        return

    cwd = os.path.abspath(".")
    
    # 1. Rasterize Lo-Fi Purple Background 2560x1440
    bg_svg = os.path.join(cwd, "assets/lofi_purple_waves_bg.svg")
    bg_png = os.path.join(cwd, "assets/lofi_purple_waves_bg.png")

    with open(bg_svg, "r", encoding="utf-8") as f:
        svg_content = f.read()

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:#080412;width:100vw;height:100vh;overflow:hidden;}} svg{{width:100vw;height:100vh;}}</style>
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
            "--window-size=2560,1440",
            f"--screenshot={bg_png}",
            "file:///" + tmp_path.replace("\\", "/")
        ]
        subprocess.run(cmd, check=True)
        print(f"[OK] Rasterized Lo-Fi Background: {bg_png}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 2. Rasterize Logo with Lo-Fi Dark Purple matching background so NO white artifacts ever appear!
    logo_svg = os.path.join(cwd, "assets/sentinel_shield_logo.svg")
    logo_png = os.path.join(cwd, "assets/sentinel_shield_logo.png")

    with open(logo_svg, "r", encoding="utf-8") as f:
        svg_logo_content = f.read()

    # Dark Lo-Fi Purple background matching the slide cards!
    html_logo = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>*{{margin:0;padding:0;box-sizing:border-box;}} body{{background:#120826;width:100vw;height:100vh;overflow:hidden;display:flex;align-items:center;justify-content:center;}} svg{{width:96vw;height:96vh;}}</style>
    </head><body>{svg_logo_content}</body></html>"""

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html_logo)
        tmp_path_logo = tmp.name

    try:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--window-size=1600,1600",
            f"--screenshot={logo_png}",
            "file:///" + tmp_path_logo.replace("\\", "/")
        ]
        subprocess.run(cmd, check=True)
        print(f"[OK] Rasterized Sentinel Logo (Lo-Fi Purple Dark): {logo_png}")
    finally:
        if os.path.exists(tmp_path_logo):
            os.remove(tmp_path_logo)

if __name__ == "__main__":
    generate_lofi_background_svg()
    rasterize_all()
