import os
import math
from PIL import Image, ImageDraw, ImageFont

def create_flow_and_logo_gif():
    width, height = 860, 540
    cx, cy = width // 2, height // 2
    
    # Load fonts (larger and bolder)
    try:
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 22)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 12)
        font_card_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 14)
        font_card_body = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 12)
        font_badge = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 11)
        font_logo_big = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 28)
        font_logo_sub = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 13)
        font_logo_foot = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 10)
    except Exception:
        font_title = font_sub = font_card_title = font_card_body = font_badge = font_logo_big = font_logo_sub = font_logo_foot = ImageFont.load_default()

    # Load high-res logo to overlay in the reveal phase
    logo_path = "assets/sentinel_shield_logo.png"
    logo_img = None
    if os.path.exists(logo_path):
        raw_logo = Image.open(logo_path).convert("RGBA")
        logo_img = raw_logo.resize((440, 440), Image.Resampling.LANCZOS)

    frames = []
    total_frames = 105

    # Node positions for Architecture Flow (Streamlined, clean, spacious)
    nodes = [
        {"name": "01. AMENAZA WAN", "sub": "Inyecciones SQLi & Fuzzing", "tag": "ATTACK INGRESS", "x": 45, "y": 85, "w": 200, "h": 110, "color": (255, 30, 86)},
        {"name": "02. pfSense IPS", "sub": "Suricata Netmap Inline Drop", "tag": "PACKET BLOCKED", "x": 330, "y": 75, "w": 205, "h": 125, "color": (0, 245, 255)},
        {"name": "03. HAProxy DMZ", "sub": "Proxy SSL + DVWA Aislada", "tag": "VLAN 20 PROTECTED", "x": 615, "y": 85, "w": 200, "h": 110, "color": (16, 185, 129)},
        {"name": "04. pfctl ENGINE", "sub": "Filtro Antiruido (>50%)", "tag": "SQLi CONFIRMED", "x": 160, "y": 275, "w": 240, "h": 125, "color": (245, 158, 11)},
        {"name": "05. VOZ IA & PBX", "sub": "Asterisk + Gemini Live 3.1", "tag": "AUTO-DIAL ACTIVE", "x": 460, "y": 275, "w": 235, "h": 125, "color": (168, 85, 247)},
        {"name": "06. CISO COMMAND", "sub": "Atención y Mitigación", "tag": "CALL ESTABLISHED", "x": 725, "y": 285, "w": 110, "h": 110, "color": (16, 185, 129)}
    ]

    for f in range(total_frames):
        # 1. Base dark canvas
        img = Image.new("RGB", (width, height), (7, 11, 18))
        draw = ImageDraw.Draw(img)

        # 2. Cyber Grid
        grid_spacing = 30
        for gx in range(0, width, grid_spacing):
            draw.line([(gx, 0), (gx, height)], fill=(16, 26, 42), width=1)
        for gy in range(0, height, grid_spacing):
            draw.line([(0, gy), (width, gy)], fill=(16, 26, 42), width=1)

        # Scanner line
        scan_y = (f * 10) % height
        draw.line([(0, scan_y), (width, scan_y)], fill=(0, 245, 255), width=1)
        draw.line([(0, (scan_y - 1) % height), (width, (scan_y - 1) % height)], fill=(0, 100, 160), width=1)

        # Tech Corner Brackets
        margin = 14
        bracket_len = 24
        draw.line([(margin, margin), (margin + bracket_len, margin)], fill=(0, 245, 255), width=2)
        draw.line([(margin, margin), (margin, margin + bracket_len)], fill=(0, 245, 255), width=2)
        draw.line([(width - margin, margin), (width - margin - bracket_len, margin)], fill=(0, 245, 255), width=2)
        draw.line([(width - margin, margin), (width - margin, margin + bracket_len)], fill=(0, 245, 255), width=2)
        draw.line([(margin, height - margin), (margin + bracket_len, height - margin)], fill=(0, 245, 255), width=2)
        draw.line([(margin, height - margin), (margin, height - margin - bracket_len)], fill=(0, 245, 255), width=2)
        draw.line([(width - margin, height - margin), (width - margin - bracket_len, height - margin)], fill=(0, 245, 255), width=2)
        draw.line([(width - margin, height - margin), (width - margin, height - margin - bracket_len)], fill=(0, 245, 255), width=2)

        # Top Banner
        draw.text((cx, 24), "KRONOS SENTINEL : FLUJO DE DEFENSA AUTÓNOMA", fill=(255, 255, 255), font=font_title, anchor="mm")
        
        if f < 15:
            status_text = "PASO 1: INICIALIZACIÓN DE LA MALLA DE SEGURIDAD..."
        elif f < 30:
            status_text = "PASO 2: INSPECCIÓN INLINE NETMAP & DROP EN pfSense..."
        elif f < 45:
            status_text = "PASO 3: CORRELACIÓN pfctl & SUPRESIÓN DE FALSOS POSITIVOS..."
        elif f < 60:
            status_text = "PASO 4: ACTIVACIÓN DE VOZ IA GEMINI LIVE & ASTERISK PBX..."
        elif f < 72:
            status_text = "CONVERGENCIA DE TELEMETRÍA Y DEFENSA PERIMETRAL..."
        else:
            status_text = "KRONOS SENTINEL ARMADO // PROTECCIÓN PERIMETRAL TOTAL"
            
        draw.text((cx, 46), status_text, fill=(0, 245, 255), font=font_sub, anchor="mm")

        # -------------------------------------------------------------
        # ACT I: FLOW CONSTRUCTION (Frames 0 to 62)
        # -------------------------------------------------------------
        if f <= 64:
            # Draw Pipelines
            # Pipe 1 -> 2
            if f >= 10:
                prog1 = min(1.0, (f - 10) / 6.0)
                p1_x = 245 + int(85 * prog1)
                draw.line([(245, 140), (p1_x, 140)], fill=(255, 30, 86), width=3)
                if prog1 > 0.4:
                    draw.text((288, 122), "WAN", fill=(255, 128, 155), font=font_badge, anchor="mm")

            # Pipe 2 -> 3
            if f >= 20:
                prog2 = min(1.0, (f - 20) / 6.0)
                p2_x = 535 + int(80 * prog2)
                draw.line([(535, 140), (p2_x, 140)], fill=(0, 245, 255), width=3)
                if prog2 > 0.4:
                    draw.text((575, 122), "DMZ", fill=(0, 245, 255), font=font_badge, anchor="mm")

            # Pipe 2 -> 4 (Downward telemetry)
            if f >= 28:
                prog3 = min(1.0, (f - 28) / 6.0)
                p3_y = 200 + int(75 * prog3)
                draw.line([(430, 200), (280, 275)], fill=(0, 245, 255), width=3)
                if prog3 > 0.4:
                    draw.text((360, 230), "eve.json", fill=(56, 189, 248), font=font_badge, anchor="mm")

            # Pipe 4 -> 5 (SOAR Trigger)
            if f >= 38:
                prog4 = min(1.0, (f - 38) / 6.0)
                p4_x = 400 + int(60 * prog4)
                draw.line([(400, 335), (p4_x, 335)], fill=(245, 158, 11), width=3)
                if prog4 > 0.4:
                    draw.text((430, 318), "HOOK", fill=(251, 191, 36), font=font_badge, anchor="mm")

            # Pipe 5 -> 6 (VoIP Dial)
            if f >= 48:
                prog5 = min(1.0, (f - 48) / 6.0)
                p5_x = 695 + int(30 * prog5)
                draw.line([(695, 335), (p5_x, 335)], fill=(16, 185, 129), width=3)
                if prog5 > 0.4:
                    draw.text((710, 318), "SIP", fill=(52, 211, 153), font=font_badge, anchor="mm")

            # Draw Nodes
            for idx, node in enumerate(nodes):
                spawn_frame = idx * 10
                if f >= spawn_frame:
                    nx, ny, nw, nh = node["x"], node["y"], node["w"], node["h"]
                    col = node["color"]
                    
                    # Box fill & outline
                    draw.rectangle([nx, ny, nx + nw, ny + nh], fill=(12, 18, 28), outline=col, width=2)
                    draw.rectangle([nx, ny, nx + nw, ny + 28], fill=col)
                    draw.text((nx + nw // 2, ny + 14), node["name"], fill=(0, 0, 0) if col == (0, 245, 255) else (255, 255, 255), font=font_card_title, anchor="mm")
                    
                    # Subtitle (clean, single impactful line)
                    draw.text((nx + nw // 2, ny + 48), node["sub"], fill=(226, 232, 240), font=font_card_body, anchor="mm")

                    # Status Tag badge
                    tag_bg = (30, 8, 14) if idx == 0 else ((4, 25, 40) if idx == 1 else ((4, 30, 20) if idx in [2, 5] else ((30, 18, 4) if idx == 3 else (25, 8, 45))))
                    draw.rectangle([nx + 10, ny + 72, nx + nw - 10, ny + 98], fill=tag_bg, outline=col, width=1)
                    draw.text((nx + nw // 2, ny + 85), node["tag"], fill=col, font=font_badge, anchor="mm")

        # -------------------------------------------------------------
        # ACT II: CONVERGENCE & ENERGY SINGULARITY (Frames 62 to 74)
        # -------------------------------------------------------------
        if 62 <= f <= 76:
            conv_t = (f - 62) / 12.0
            # Laser beams shooting from all nodes to center
            for node in nodes:
                nx_center = node["x"] + node["w"] // 2
                ny_center = node["y"] + node["h"] // 2
                cur_x = int(nx_center + (cx - nx_center) * conv_t)
                cur_y = int(ny_center + (cy - ny_center) * conv_t)
                draw.line([(nx_center, ny_center), (cur_x, cur_y)], fill=node["color"], width=3)
                draw.ellipse([cur_x - 6, cur_y - 6, cur_x + 6, cur_y + 6], fill=(255, 255, 255), outline=node["color"])

            # Center Singularity Flare
            flare_r = max(4, int(12 + 70 * max(0.0, math.sin(conv_t * math.pi))))
            draw.ellipse([cx - flare_r, cy - flare_r, cx + flare_r, cy + flare_r], fill=(0, 245, 255), outline=(255, 255, 255), width=2)
            draw.ellipse([cx - flare_r // 2, cy - flare_r // 2, cx + flare_r // 2, cy + flare_r // 2], fill=(255, 255, 255))

        # -------------------------------------------------------------
        # ACT III & IV: BIRTH & MAJESTY OF THE LOGO (Frames 72 to 104)
        # -------------------------------------------------------------
        if f >= 72:
            logo_t = min(1.0, (f - 72) / 12.0)
            
            # Rotating HUD target rings
            ring_rot = (f * 4) % 360
            r1 = max(10, int(185 * logo_t))
            r2 = max(15, int(225 * logo_t))
            
            # Outer cyber HUD rings
            draw.arc([cx - r2, cy - r2, cx + r2, cy + r2], start=ring_rot, end=ring_rot + 120, fill=(0, 245, 255), width=2)
            draw.arc([cx - r2, cy - r2, cx + r2, cy + r2], start=ring_rot + 180, end=ring_rot + 300, fill=(0, 245, 255), width=2)
            draw.arc([cx - r1, cy - r1, cx + r1, cy + r1], start=-ring_rot, end=-ring_rot + 90, fill=(255, 30, 86), width=2)
            draw.arc([cx - r1, cy - r1, cx + r1, cy + r1], start=-ring_rot + 180, end=-ring_rot + 270, fill=(255, 30, 86), width=2)

            # Draw Logo image overlay with alpha
            if logo_img and logo_t > 0.05:
                pulse = 1.0 + (0.025 * math.sin((f - 72) * 0.35) if f > 82 else 0)
                current_size = max(10, int(360 * logo_t * pulse))
                resized_logo = logo_img.resize((current_size, current_size), Image.Resampling.LANCZOS)
                
                pos_x = cx - current_size // 2
                pos_y = cy - current_size // 2 - 12
                img.paste(resized_logo, (pos_x, pos_y), resized_logo)

            # Pulsing Voice Waveform Indicators at the base
            if f >= 80:
                wave_amp = int(7 * math.sin(f * 0.6))
                for wi in range(-4, 5):
                    bar_h = 10 + abs(wi) * 4 + wave_amp
                    bx = cx + wi * 14
                    draw.line([(bx, 440 - bar_h), (bx, 440 + bar_h)], fill=(0, 245, 255), width=3)

            # Reveal Text Banner
            if f >= 82:
                draw.text((cx, 475), "KRONOS SENTINEL", fill=(255, 255, 255), font=font_logo_big, anchor="mm")
                draw.text((cx, 500), "AUTONOMOUS AI-IPS • LIVE VOICE SOAR • pfSense", fill=(0, 245, 255), font=font_logo_sub, anchor="mm")
                draw.text((cx, 518), "DUOC UC SAN JOAQUÍN • INGENIERÍA EN CONECTIVIDAD Y REDES", fill=(148, 163, 184), font=font_logo_foot, anchor="mm")

        # Bottom footer protocol
        draw.text((cx, height - 10), "FREEBSD 14 / pfSense CE • SURICATA NETMAP • pfctl SNORT2C • ASTERISK PBX • GEMINI LIVE 3.1", fill=(100, 116, 139), font=font_badge, anchor="mm")

        # Quantize frame for crisp 256-color palette
        frame_quantized = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        frames.append(frame_quantized)

    output_gif = "assets/kronos_sentinel_flow_build.gif"
    # Duration: 80ms per frame, last frame held for 3000ms
    durations = [80] * (total_frames - 1) + [3000]
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Generated {output_gif} ({os.path.getsize(output_gif)} bytes, {total_frames} frames, ~11.5s total duration)")

if __name__ == "__main__":
    create_flow_and_logo_gif()

