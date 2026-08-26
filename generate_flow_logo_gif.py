import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_flow_and_logo_gif():
    width, height = 860, 540
    cx, cy = width // 2, height // 2
    
    # Load fonts
    try:
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 20)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 11)
        font_card_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 12)
        font_card_body = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 10)
        font_badge = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 9)
        font_logo_big = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 26)
        font_logo_sub = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 11)
        font_logo_foot = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 9)
    except Exception:
        font_title = font_sub = font_card_title = font_card_body = font_badge = font_logo_big = font_logo_sub = font_logo_foot = ImageFont.load_default()

    # Load high-res logo to overlay in the reveal phase
    logo_path = "assets/sentinel_shield_logo.png"
    logo_img = None
    if os.path.exists(logo_path):
        raw_logo = Image.open(logo_path).convert("RGBA")
        logo_img = raw_logo.resize((420, 420), Image.Resampling.LANCZOS)

    frames = []
    total_frames = 72

    # Node positions for Architecture Flow
    nodes = [
        {"name": "01. THREAT INGRESS", "sub": "SQLi & Exploit Vectors", "x": 40, "y": 80, "w": 180, "h": 120, "color": (255, 30, 86)},
        {"name": "02. pfSense NETMAP", "sub": "Suricata Inline IPS Drop", "x": 280, "y": 70, "w": 200, "h": 140, "color": (0, 245, 255)},
        {"name": "03. HAProxy DMZ", "sub": "SSL Term & DVWA Lab", "x": 540, "y": 80, "w": 170, "h": 120, "color": (16, 185, 129)},
        {"name": "04. pfctl ENGINE", "sub": "Filtro Antiruido (>50%)", "x": 220, "y": 280, "w": 220, "h": 140, "color": (245, 158, 11)},
        {"name": "05. VOICE SOAR", "sub": "Asterisk & Gemini Live", "x": 510, "y": 280, "w": 190, "h": 140, "color": (168, 85, 247)},
        {"name": "06. CISO COMMAND", "sub": "Llamada de Voz en Vivo", "x": 730, "y": 290, "w": 105, "h": 120, "color": (16, 185, 129)}
    ]

    for f in range(total_frames):
        # 1. Base dark canvas
        img = Image.new("RGB", (width, height), (7, 11, 18))
        draw = ImageDraw.Draw(img)

        # 2. Cyber Grid
        grid_spacing = 30
        grid_offset = (f * 2) % grid_spacing
        for gx in range(0, width, grid_spacing):
            draw.line([(gx, 0), (gx, height)], fill=(16, 26, 42), width=1)
        for gy in range(0, height, grid_spacing):
            draw.line([(0, gy), (width, gy)], fill=(16, 26, 42), width=1)

        # Scanner line
        scan_y = (f * 14) % height
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
        draw.text((cx, 24), "KRONOS SENTINEL : SEC-OPS AUTONOMOUS PIPELINE", fill=(255, 255, 255), font=font_title, anchor="mm")
        status_text = "INITIALIZING DEFENSE GRID..." if f < 10 else ("CONSTRUCTING INCIDENT TELEMETRY FLOW..." if f < 35 else ("CONVERGING DEFENSE VECTORS..." if f < 48 else "KRONOS SENTINEL ONLINE // ALL SYSTEMS ARMED"))
        draw.text((cx, 44), status_text, fill=(0, 245, 255), font=font_sub, anchor="mm")

        # -------------------------------------------------------------
        # ACT I: FLOW CONSTRUCTION (Frames 0 to 35)
        # -------------------------------------------------------------
        if f <= 44:
            # Draw Pipes & Connectors
            # Pipe 1 -> 2
            if f >= 6:
                progress = min(1.0, (f - 6) / 5.0)
                p1_x = 220 + int(60 * progress)
                draw.line([(220, 140), (p1_x, 140)], fill=(255, 30, 86), width=3)
                if progress > 0.3:
                    draw.text((250, 125), "WAN", fill=(255, 128, 155), font=font_badge, anchor="mm")

            # Pipe 2 -> 3
            if f >= 12:
                progress = min(1.0, (f - 12) / 5.0)
                p2_x = 480 + int(60 * progress)
                draw.line([(480, 140), (p2_x, 140)], fill=(0, 245, 255), width=3)
                if progress > 0.3:
                    draw.text((510, 125), "DMZ", fill=(0, 245, 255), font=font_badge, anchor="mm")

            # Pipe 2 -> 4 (Downward telemetry)
            if f >= 16:
                progress = min(1.0, (f - 16) / 5.0)
                p3_y = 210 + int(70 * progress)
                draw.line([(380, 210), (380, p3_y)], fill=(0, 245, 255), width=3)
                if progress > 0.4:
                    draw.text((380, 245), "eve.json", fill=(56, 189, 248), font=font_badge, anchor="mm")

            # Pipe 4 -> 5 (SOAR Trigger)
            if f >= 22:
                progress = min(1.0, (f - 22) / 5.0)
                p4_x = 440 + int(70 * progress)
                draw.line([(440, 350), (p4_x, 350)], fill=(245, 158, 11), width=3)
                if progress > 0.4:
                    draw.text((475, 335), "HOOK", fill=(251, 191, 36), font=font_badge, anchor="mm")

            # Pipe 5 -> 6 (VoIP Dial)
            if f >= 28:
                progress = min(1.0, (f - 28) / 5.0)
                p5_x = 700 + int(30 * progress)
                draw.line([(700, 350), (p5_x, 350)], fill=(16, 185, 129), width=3)
                if progress > 0.4:
                    draw.text((715, 335), "SIP", fill=(52, 211, 153), font=font_badge, anchor="mm")

            # Draw Nodes
            for idx, node in enumerate(nodes):
                spawn_frame = idx * 6
                if f >= spawn_frame:
                    alpha_ratio = min(1.0, (f - spawn_frame) / 4.0)
                    nx, ny, nw, nh = node["x"], node["y"], node["w"], node["h"]
                    col = node["color"]
                    
                    # Box fill & outline
                    draw.rectangle([nx, ny, nx + nw, ny + nh], fill=(12, 18, 28), outline=col, width=2)
                    draw.rectangle([nx, ny, nx + nw, ny + 24], fill=col)
                    draw.text((nx + nw // 2, ny + 12), node["name"], fill=(0, 0, 0) if col == (0, 245, 255) else (255, 255, 255), font=font_card_title, anchor="mm")
                    draw.text((nx + 10, ny + 38), node["sub"], fill=(226, 232, 240), font=font_card_body)

                    # Sub details
                    if idx == 0:
                        draw.text((nx + 10, ny + 58), "• SQL Injection Payloads", fill=(255, 128, 155), font=font_card_body)
                        draw.text((nx + 10, ny + 74), "• Automated Scanners", fill=(200, 200, 200), font=font_card_body)
                        draw.rectangle([nx + 8, ny + 94, nx + nw - 8, ny + 112], fill=(40, 8, 16), outline=(255, 30, 86))
                        draw.text((nx + nw // 2, ny + 103), "UNTRUSTED WAN", fill=(255, 77, 109), font=font_badge, anchor="mm")
                    elif idx == 1:
                        draw.text((nx + 10, ny + 58), "• pfBlockerNG GeoIP", fill=(0, 245, 255), font=font_card_body)
                        draw.text((nx + 10, ny + 74), "• Netmap Ring Buffer Drop", fill=(200, 200, 200), font=font_card_body)
                        draw.text((nx + 10, ny + 90), "• snort2c Blackholing", fill=(52, 211, 153), font=font_card_body)
                        draw.rectangle([nx + 8, ny + 112, nx + nw - 8, ny + 132], fill=(4, 27, 45), outline=(0, 245, 255))
                        draw.text((nx + nw // 2, ny + 122), "ZERO LATENCY IPS DROP", fill=(16, 185, 129), font=font_badge, anchor="mm")
                    elif idx == 2:
                        draw.text((nx + 10, ny + 58), "• HAProxy SSL Offload", fill=(52, 211, 153), font=font_card_body)
                        draw.text((nx + 10, ny + 74), "• DVWA Container Lab", fill=(251, 191, 36), font=font_card_body)
                        draw.rectangle([nx + 8, ny + 94, nx + nw - 8, ny + 112], fill=(4, 38, 24), outline=(16, 185, 129))
                        draw.text((nx + nw // 2, ny + 103), "DMZ VLAN 20", fill=(110, 231, 183), font=font_badge, anchor="mm")
                    elif idx == 3:
                        draw.text((nx + 10, ny + 58), "• Parser continuo eve.json", fill=(251, 191, 36), font=font_card_body)
                        draw.text((nx + 10, ny + 74), "• Heurística Anti-FP >50%", fill=(52, 211, 153), font=font_card_body)
                        draw.text((nx + 10, ny + 90), "• Test atómico pfctl kernel", fill=(56, 189, 248), font=font_card_body)
                        draw.rectangle([nx + 8, ny + 112, nx + nw - 8, ny + 132], fill=(30, 20, 4), outline=(245, 158, 11))
                        draw.text((nx + nw // 2, ny + 122), "ATAQUE REAL CONFIRMADO", fill=(253, 230, 138), font=font_badge, anchor="mm")
                    elif idx == 4:
                        draw.text((nx + 10, ny + 58), "• Asterisk PBX AMI Dialer", fill=(216, 180, 254), font=font_card_body)
                        draw.text((nx + 10, ny + 74), "• Gemini Live Flash 3.1", fill=(0, 245, 255), font=font_card_body)
                        draw.text((nx + 10, ny + 90), "• Audio Bridge WebSocket", fill=(255, 128, 155), font=font_card_body)
                        draw.rectangle([nx + 8, ny + 112, nx + nw - 8, ny + 132], fill=(28, 9, 51), outline=(168, 85, 247))
                        draw.text((nx + nw // 2, ny + 122), "LLAMADA EN TIEMPO REAL", fill=(233, 213, 255), font=font_badge, anchor="mm")
                    elif idx == 5:
                        draw.text((nx + 6, ny + 58), "• Teléfono CISO", fill=(52, 211, 153), font=font_card_body)
                        draw.text((nx + 6, ny + 74), "• Voz con IA", fill=(255, 255, 255), font=font_card_body)
                        draw.rectangle([nx + 6, ny + 94, nx + nw - 6, ny + 112], fill=(4, 38, 24), outline=(16, 185, 129))
                        draw.text((nx + nw // 2, ny + 103), "ENLACE ACTIVO", fill=(167, 243, 208), font=font_badge, anchor="mm")

        # -------------------------------------------------------------
        # ACT II: CONVERGENCE & ENERGY SINGULARITY (Frames 36 to 48)
        # -------------------------------------------------------------
        if 36 <= f <= 50:
            conv_t = (f - 36) / 12.0
            # Laser beams shooting from all nodes to center
            for node in nodes:
                nx_center = node["x"] + node["w"] // 2
                ny_center = node["y"] + node["h"] // 2
                cur_x = int(nx_center + (cx - nx_center) * conv_t)
                cur_y = int(ny_center + (cy - ny_center) * conv_t)
                draw.line([(nx_center, ny_center), (cur_x, cur_y)], fill=node["color"], width=3)
                draw.ellipse([cur_x - 5, cur_y - 5, cur_x + 5, cur_y + 5], fill=(255, 255, 255), outline=node["color"])

            # Center Singularity Flare
            flare_r = max(4, int(10 + 60 * max(0.0, math.sin(conv_t * math.pi))))
            draw.ellipse([cx - flare_r, cy - flare_r, cx + flare_r, cy + flare_r], fill=(0, 245, 255), outline=(255, 255, 255), width=2)
            draw.ellipse([cx - flare_r // 2, cy - flare_r // 2, cx + flare_r // 2, cy + flare_r // 2], fill=(255, 255, 255))

        # -------------------------------------------------------------
        # ACT III: BIRTH OF THE KRONOS SENTINEL SHIELD LOGO (Frames 47 to 71)
        # -------------------------------------------------------------
        if f >= 46:
            logo_t = min(1.0, (f - 46) / 14.0)
            
            # Rotating HUD target rings
            ring_rot = (f * 5) % 360
            r1 = max(10, int(180 * logo_t))
            r2 = max(15, int(220 * logo_t))
            
            # Outer cyber HUD rings
            draw.arc([cx - r2, cy - r2, cx + r2, cy + r2], start=ring_rot, end=ring_rot + 120, fill=(0, 245, 255), width=2)
            draw.arc([cx - r2, cy - r2, cx + r2, cy + r2], start=ring_rot + 180, end=ring_rot + 300, fill=(0, 245, 255), width=2)
            draw.arc([cx - r1, cy - r1, cx + r1, cy + r1], start=-ring_rot, end=-ring_rot + 90, fill=(255, 30, 86), width=2)
            draw.arc([cx - r1, cy - r1, cx + r1, cy + r1], start=-ring_rot + 180, end=-ring_rot + 270, fill=(255, 30, 86), width=2)

            # Draw Logo image overlay with alpha
            if logo_img and logo_t > 0.05:
                # Calculate scale & pulse
                pulse = 1.0 + (0.03 * math.sin((f - 46) * 0.4) if f > 60 else 0)
                current_size = max(10, int(360 * logo_t * pulse))
                resized_logo = logo_img.resize((current_size, current_size), Image.Resampling.LANCZOS)
                
                # Center paste with alpha
                pos_x = cx - current_size // 2
                pos_y = cy - current_size // 2 - 10
                img.paste(resized_logo, (pos_x, pos_y), resized_logo)

            # Pulsing Voice Waveform Indicators at the base
            if f >= 54:
                wave_amp = int(8 * math.sin(f * 0.8))
                for wi in range(-4, 5):
                    bar_h = 10 + abs(wi) * 4 + wave_amp
                    bx = cx + wi * 14
                    draw.line([(bx, 440 - bar_h), (bx, 440 + bar_h)], fill=(0, 245, 255), width=3)

            # Reveal Text Banner
            if f >= 56:
                draw.text((cx, 475), "KRONOS SENTINEL", fill=(255, 255, 255), font=font_logo_big, anchor="mm")
                draw.text((cx, 500), "AUTONOMOUS AI-IPS • LIVE VOICE SOAR • pfSense", fill=(0, 245, 255), font=font_logo_sub, anchor="mm")
                draw.text((cx, 518), "DUOC UC SAN JOAQUÍN • INGENIERÍA EN CONECTIVIDAD Y REDES", fill=(148, 163, 184), font=font_logo_foot, anchor="mm")

        # Bottom footer protocol
        draw.text((cx, height - 10), "FREEBSD 14 / pfSense CE • SURICATA NETMAP • pfctl SNORT2C • ASTERISK PBX • GEMINI LIVE 3.1", fill=(100, 116, 139), font=font_badge, anchor="mm")

        # Quantize frame for crisp 256-color palette
        frame_quantized = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        frames.append(frame_quantized)

    output_gif = "assets/kronos_sentinel_flow_build.gif"
    # Duration: 70ms per frame, last frame held for 1800ms
    durations = [70] * (total_frames - 1) + [1800]
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Generated {output_gif} ({os.path.getsize(output_gif)} bytes, {total_frames} frames)")

if __name__ == "__main__":
    create_flow_and_logo_gif()
