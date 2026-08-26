#!/usr/bin/env python3
"""
KRONOS SENTINEL - High-Tech Animated Process Flow GIF Generator
Generates a dynamic, cyber-aesthetic, looping animated GIF showing the complete
attack flow, kernel pfctl containment, KRONOS AST correlation, Asterisk dialing,
and Gemini Live AI Voice debriefing in real-time.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

WIDTH = 980
HEIGHT = 560
TOTAL_FRAMES = 64
FRAME_DURATION = 110  # ms per frame (~7.0s full cycle)
OUTPUT_PATH = "assets/kronos_process_flow.gif"

# Paleta Cromática SecOps
BG_DARK = (7, 10, 17)
BG_CARD = (13, 21, 39)
BG_CARD_HEADER = (17, 28, 52)
BORDER_DIM = (30, 41, 59)
BORDER_ACTIVE = (56, 189, 248)

CYAN_NEON = (0, 245, 255)
CYAN_GLOW = (56, 189, 248)
RED_HOSTILE = (255, 30, 86)
RED_GLOW = (244, 63, 94)
AMBER_WARN = (245, 158, 11)
AMBER_GLOW = (251, 191, 36)
GREEN_SECURE = (16, 185, 129)
GREEN_GLOW = (52, 211, 153)
PURPLE_AI = (168, 85, 247)
PURPLE_GLOW = (192, 132, 252)

TEXT_WHITE = (248, 250, 252)
TEXT_LIGHT = (226, 232, 240)
TEXT_MUTED = (148, 163, 184)
TEXT_DARK = (100, 116, 139)

def load_fonts():
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 15)
        font_header = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 12)
        font_body = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 10)
        font_mono = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 9)
        font_mono_bold = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 10)
        font_badge = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 9)
    except Exception:
        font_title = ImageFont.load_default()
        font_header = font_title
        font_body = font_title
        font_mono = font_title
        font_mono_bold = font_title
        font_badge = font_title
    return {
        "title": font_title,
        "header": font_header,
        "body": font_body,
        "mono": font_mono,
        "mono_bold": font_mono_bold,
        "badge": font_badge
    }

def draw_rounded_rect(draw, bbox, radius, fill, outline, width=1):
    x0, y0, x1, y1 = bbox
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def draw_card(draw, bbox, title, step_num, active_color, is_active, fonts, lines_text=None, badge_text=None, badge_color=None):
    x0, y0, x1, y1 = bbox
    header_h = 24
    
    # Border & Fill
    border_c = active_color if is_active else BORDER_DIM
    border_w = 2 if is_active else 1
    bg_c = (BG_CARD[0]+10, BG_CARD[1]+10, BG_CARD[2]+15) if is_active else BG_CARD
    
    draw_rounded_rect(draw, [x0, y0, x1, y1], 6, fill=bg_c, outline=border_c, width=border_w)
    
    # Header Bar
    hdr_fill = (active_color[0]//4, active_color[1]//4, active_color[2]//4) if is_active else BG_CARD_HEADER
    draw.rounded_rectangle([x0, y0, x1, y0 + header_h], radius=6, fill=hdr_fill)
    draw.rectangle([x0, y0 + header_h - 4, x1, y0 + header_h], fill=hdr_fill)
    
    # Header Text
    hdr_title = f"{step_num} {title}"
    draw.text((x0 + 8, y0 + 5), hdr_title, fill=TEXT_WHITE if is_active else TEXT_LIGHT, font=fonts["header"])
    
    # Active indicator dot
    dot_c = active_color if is_active else TEXT_DARK
    draw.ellipse([x1 - 16, y0 + 8, x1 - 8, y0 + 16], fill=dot_c)
    
    # Lines
    if lines_text:
        curr_y = y0 + header_h + 8
        for line, is_bold, color in lines_text:
            f = fonts["mono_bold"] if is_bold else fonts["mono"]
            c = color if color else (TEXT_LIGHT if is_active else TEXT_MUTED)
            draw.text((x0 + 8, curr_y), line, fill=c, font=f)
            curr_y += 14
            
    # Badge at bottom of card
    if badge_text and badge_color:
        b_w = len(badge_text) * 6 + 12
        b_h = 16
        bx0 = x0 + 8
        by0 = y1 - b_h - 6
        draw_rounded_rect(draw, [bx0, by0, bx0 + b_w, by0 + b_h], 3, fill=(badge_color[0]//4, badge_color[1]//4, badge_color[2]//4), outline=badge_color, width=1)
        draw.text((bx0 + 6, by0 + 2), badge_text, fill=badge_color, font=fonts["badge"])

def generate_frame(f_idx, fonts):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    
    # -------------------------------------------------------------
    # 1. Subtle Background Grid & Coordinates
    # -------------------------------------------------------------
    for x in range(0, WIDTH, 35):
        draw.line([(x, 0), (x, HEIGHT)], fill=(12, 17, 28), width=1)
    for y in range(0, HEIGHT, 35):
        draw.line([(0, y), (WIDTH, y)], fill=(12, 17, 28), width=1)
        
    # -------------------------------------------------------------
    # 2. Top Header HUD
    # -------------------------------------------------------------
    pulse_val = (math.sin(f_idx * 0.2) + 1) / 2
    pulse_cyan = (int(0 + 56 * pulse_val), int(200 + 45 * pulse_val), 255)
    
    draw.text((30, 14), "KRONOS SENTINEL", fill=pulse_cyan, font=fonts["title"])
    draw.text((205, 16), " // REAL-TIME ATTACK FLOW & SOAR RESPONSE PIPELINE", fill=TEXT_MUTED, font=fonts["mono_bold"])
    
    # Live Status Badge
    draw_rounded_rect(draw, [WIDTH - 210, 12, WIDTH - 30, 32], 4, fill=(10, 30, 20), outline=GREEN_SECURE, width=1)
    draw.ellipse([WIDTH - 200, 19, WIDTH - 192, 27], fill=GREEN_SECURE)
    draw.text((WIDTH - 184, 16), "LIVE SOC MONITORING", fill=GREEN_GLOW, font=fonts["badge"])
    
    draw.line([(30, 42), (WIDTH - 30, 42)], fill=BORDER_DIM, width=1)
    draw.line([(30, 42), (30 + int((WIDTH - 60) * (f_idx / TOTAL_FRAMES)), 42)], fill=CYAN_NEON, width=2)
    
    # -------------------------------------------------------------
    # 3. State Determination by Frame Index
    # -------------------------------------------------------------
    # 0 - 12: Phase 1 (Hostile Ingress)
    # 13 - 26: Phase 2 (Suricata Netmap IPS & pfctl Kill States)
    # 27 - 40: Phase 3 (KRONOS AST Correlation & Anti-Noise)
    # 41 - 52: Phase 4 (Asterisk 20 PBX Auto-Dialer)
    # 53 - 63: Phase 5 (Gemini Live AI Voice Debriefing)
    
    p1_active = 0 <= f_idx <= 14
    p2_active = 12 <= f_idx <= 28
    p3_active = 26 <= f_idx <= 42
    p4_active = 40 <= f_idx <= 54
    p5_active = 52 <= f_idx <= 63
    
    # -------------------------------------------------------------
    # 4. Bus Pipelines & Connectors
    # -------------------------------------------------------------
    # Pipe 1: WAN -> pfSense
    draw.line([(200, 130), (280, 130)], fill=RED_HOSTILE if p1_active else BORDER_DIM, width=2)
    if p1_active:
        pct = (f_idx % 14) / 14.0
        px = int(200 + 80 * pct)
        draw.ellipse([px - 4, 126, px + 4, 134], fill=RED_HOSTILE)
        draw.text((215, 114), "SQLi", fill=RED_GLOW, font=fonts["mono"])
        
    # Pipe 2: pfSense -> DMZ HAProxy
    draw.line([(480, 130), (550, 130)], fill=CYAN_NEON if p2_active else BORDER_DIM, width=2)
    if p2_active:
        pct = ((f_idx - 12) % 15) / 15.0
        px = int(480 + 70 * pct)
        draw.ellipse([px - 4, 126, px + 4, 134], fill=CYAN_NEON)
        
    # Pipe 3: pfSense Down -> KRONOS Engine
    draw.line([(380, 220), (380, 280)], fill=AMBER_WARN if p2_active or p3_active else BORDER_DIM, width=2)
    if p2_active or p3_active:
        pct = ((f_idx - 20) % 15) / 15.0
        py = int(220 + 60 * pct)
        draw.ellipse([376, py - 4, 384, py + 4], fill=AMBER_WARN)
        draw.text((390, 245), "eve.json", fill=AMBER_GLOW, font=fonts["mono"])
        
    # Pipe 4: KRONOS Engine -> Asterisk PBX
    draw.line([(490, 360), (560, 360)], fill=PURPLE_AI if p3_active or p4_active else BORDER_DIM, width=2)
    if p3_active or p4_active:
        pct = ((f_idx - 35) % 15) / 15.0
        px = int(490 + 70 * pct)
        draw.ellipse([px - 4, 356, px + 4, 364], fill=PURPLE_AI)
        draw.text((505, 344), "SOAR POST", fill=PURPLE_GLOW, font=fonts["mono"])
        
    # Pipe 5: Asterisk PBX -> Gemini Voice Bridge
    draw.line([(730, 360), (790, 360)], fill=GREEN_SECURE if p4_active or p5_active else BORDER_DIM, width=2)
    if p4_active or p5_active:
        pct = ((f_idx - 48) % 15) / 15.0
        px = int(730 + 60 * pct)
        draw.ellipse([px - 4, 356, px + 4, 364], fill=GREEN_SECURE)
        draw.text((740, 344), "RTP 24kHz", fill=GREEN_GLOW, font=fonts["mono"])

    # -------------------------------------------------------------
    # 5. Render Topology Nodes
    # -------------------------------------------------------------
    
    # CARD 01: Hostile WAN Ingress
    c1_lines = [
        ("IP: 185.220.101.5 [RU]", True, RED_GLOW if p1_active else None),
        ("Vector: SQL Injection", False, None),
        ("Target: VIP HAProxy :443", False, None),
        ("Payload: admin' OR '1'='1", True, RED_HOSTILE if p1_active else None)
    ]
    draw_card(draw, [30, 55, 200, 220], "AMENAZA WAN", "01.", RED_HOSTILE, p1_active, fonts, c1_lines, 
              badge_text="HOSTILE INTRUSION" if p1_active else "IDLE SCANNER", badge_color=RED_HOSTILE if p1_active else TEXT_DARK)

    # CARD 02: pfSense CE & Suricata Netmap IPS
    c2_lines = [
        ("Suricata 7.x Inline Netmap", True, CYAN_NEON if p2_active else None),
        ("Hardware Drop: 0.04ms", False, GREEN_GLOW if p2_active else None),
        ("FreeBSD Kernel pfctl:", True, None),
        (">> pfctl -k 185.220.101.5", True, CYAN_GLOW if p2_active else None),
        (">> Table <snort2c> (RAM)", False, None)
    ]
    draw_card(draw, [280, 55, 480, 220], "pfSense & IPS NETMAP", "02.", CYAN_NEON, p2_active, fonts, c2_lines,
              badge_text="KERNEL PFCTL DROP" if p2_active else "INSPECTING RING-BUFFER", badge_color=CYAN_NEON if p2_active else TEXT_DARK)

    # CARD 03: HAProxy DMZ & DVWA
    c3_lines = [
        ("HAProxy 2.8+ SSL Offload", True, GREEN_GLOW if p2_active else None),
        ("VIP: 192.168.20.10:443", False, None),
        ("Stick-Tables: Anti-Fuzz", False, None),
        ("Backend: DVWA (VLAN 20)", True, None)
    ]
    draw_card(draw, [550, 55, 730, 220], "DMZ & DVWA LAB", "03.", GREEN_SECURE, False, fonts, c3_lines,
              badge_text="VLAN 20 ISOLATED", badge_color=GREEN_SECURE)

    # CARD 04: Motor de Correlación KRONOS
    c4_lines = [
        ("KRONOS Heuristic Engine (Py 3.12)", True, AMBER_GLOW if p3_active else None),
        ("Ingesta: eve.json Tail Stream", False, None),
        ("AST Parser: Boolean Logic True", True, AMBER_WARN if p3_active else None),
        ("Noise Filter: >50% Discarded", False, GREEN_GLOW if p3_active else None),
        ("Confidence: 94.8% Real Attack", True, RED_GLOW if p3_active else None)
    ]
    draw_card(draw, [210, 280, 490, 455], "MOTOR DE CORRELACIÓN KRONOS", "04.", AMBER_WARN, p3_active, fonts, c4_lines,
              badge_text="ATTACK VALIDATED -> TRIGGER SOAR" if p3_active else "LISTENING EVE.JSON", badge_color=AMBER_WARN if p3_active else TEXT_DARK)

    # CARD 05: Asterisk 20 LTS PBX
    c5_lines = [
        ("Asterisk 20 LTS (Docker)", True, PURPLE_GLOW if p4_active else None),
        ("AMI Originate Trigger", False, None),
        ("Channel: PJSIP/1001 (CISO)", True, PURPLE_AI if p4_active else None),
        ("Dial Status: RINGING / ANSWER", True, GREEN_GLOW if p4_active else None)
    ]
    draw_card(draw, [560, 280, 730, 455], "ASTERISK PBX", "05.", PURPLE_AI, p4_active, fonts, c5_lines,
              badge_text="CISO CALL CONNECTED" if p4_active else "TRUNK READY", badge_color=PURPLE_AI if p4_active else TEXT_DARK)

    # CARD 06: Gemini Live Voice SOAR
    c6_lines = [
        ("Gemini Live Flash 3.1", True, CYAN_NEON if p5_active else None),
        ("Mode: Bidirectional Audio", False, None),
        ("Latency: < 400ms Streaming", False, None),
        ("CISO Briefing: Active Voice", True, GREEN_GLOW if p5_active else None)
    ]
    draw_card(draw, [770, 110, 950, 455], "VOZ IA GEMINI LIVE", "06.", CYAN_NEON, p5_active, fonts, c6_lines,
              badge_text="TALKING TO CISO" if p5_active else "AWAITING DISPATCH", badge_color=GREEN_SECURE if p5_active else TEXT_DARK)

    # Audio Equalizer Bars in Gemini Card if Phase 5
    if p5_active:
        eq_base_y = 410
        for i in range(12):
            bar_h = int(8 + 18 * abs(math.sin((f_idx * 0.4) + (i * 0.5))))
            bx = 790 + i * 11
            draw.rectangle([bx, eq_base_y - bar_h, bx + 7, eq_base_y], fill=CYAN_NEON)
        draw.text((790, 420), "AUDIO PCM 24kHz", fill=CYAN_GLOW, font=fonts["mono"])

    # -------------------------------------------------------------
    # 6. Bottom Console Terminal HUD (Live Telemetry)
    # -------------------------------------------------------------
    draw_rounded_rect(draw, [30, 470, WIDTH - 30, 545], 5, fill=(10, 14, 24), outline=BORDER_DIM, width=1)
    draw.rectangle([30, 470, 160, 490], fill=(20, 30, 50))
    draw.text((40, 474), "SEC-OPS TELEMETRY LOG", fill=CYAN_NEON, font=fonts["badge"])
    
    # Active Log message depending on phase
    if p1_active:
        log_msg1 = "[T+0.00s] [INGRESS] Hostile actor 185.220.101.5 sends payload: GET /vulnerabilities/sqli/?id=1' OR '1'='1"
        log_msg2 = "[T+0.02s] [HAProxy] SSL handshake terminated on VIP 192.168.20.10:443. Forwarding to inspection."
        c_log = RED_GLOW
    elif p2_active:
        log_msg1 = "[T+0.04s] [NETMAP IPS] Suricata 7.x inline ring-buffer catches SQLi rule -> Drops packet in hardware."
        log_msg2 = "[T+0.08s] [FREEBSD KERNEL] pfctl -k 185.220.101.5 executed. Host dynamically blacklisted in <snort2c> RAM table."
        c_log = CYAN_GLOW
    elif p3_active:
        log_msg1 = "[T+0.12s] [KRONOS CORE] log_correlator tails eve.json -> Heuristic AST validates SQLi syntax tree (Score: 0.94)."
        log_msg2 = "[T+0.21s] [SOAR HOOK] pfctl -t snort2c -T test passed. Dispatched webhook POST to Voice Dispatcher daemon."
        c_log = AMBER_GLOW
    elif p4_active:
        log_msg1 = "[T+0.45s] [VOIP DIAL] Asterisk AMI executes Action: Originate -> Dialing CISO Mobile via PJSIP/1001 trunk."
        log_msg2 = "[T+0.85s] [SIP BRIDGE] Call answered. Connecting bidirectional audio RTP stream to Gemini Live Flash 3.1."
        c_log = PURPLE_GLOW
    else:  # p5_active
        log_msg1 = "[T+1.10s] [GEMINI LIVE] 'Alerta Crítica: Inyección SQL neutralizada en kernel pfSense desde 185.220.101.5.'"
        log_msg2 = "[T+1.40s] [STATUS] Threat 100% contained in kernel FreeBSD. CISO alerted by AI voice debriefing in <1.5s."
        c_log = GREEN_GLOW

    draw.text((40, 498), log_msg1, fill=c_log, font=fonts["mono_bold"])
    draw.text((40, 518), log_msg2, fill=TEXT_LIGHT, font=fonts["mono"])
    
    # Step indicator dots on right
    steps = [("WAN", p1_active), ("IPS", p2_active), ("KRONOS", p3_active), ("PBX", p4_active), ("VOICE", p5_active)]
    for s_idx, (s_name, s_act) in enumerate(steps):
        sx = WIDTH - 270 + s_idx * 46
        sy = 478
        dot_color = CYAN_NEON if s_act else (30, 45, 70)
        draw.ellipse([sx, sy + 3, sx + 6, sy + 9], fill=dot_color)
        draw.text((sx + 10, sy), s_name, fill=TEXT_WHITE if s_act else TEXT_DARK, font=fonts["badge"])

    return img

def main():
    fonts = load_fonts()
    frames = []
    
    print(f"Generating {TOTAL_FRAMES} high-tech animation frames...")
    for f in range(TOTAL_FRAMES):
        frame = generate_frame(f, fonts)
        # Convert to 256 color palette for compact GIF
        pal_frame = frame.convert("P", palette=Image.ADAPTIVE, colors=128)
        frames.append(pal_frame)
        if f % 10 == 0:
            print(f"  Frame {f}/{TOTAL_FRAMES} processed...")
            
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    frames[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION,
        loop=0,
        optimize=True
    )
    
    file_size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    print(f"[OK] High-Tech Process Flow GIF saved: {OUTPUT_PATH} ({file_size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
