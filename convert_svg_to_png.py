import os
import subprocess
import tempfile

def convert():
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ]
    browser = None
    for p in edge_paths:
        if os.path.exists(p):
            browser = p
            break
            
    if not browser:
        print("No headless browser found.")
        return

    cwd = os.path.abspath(".")
    
    def render_svg(svg_rel_path, png_rel_path, width, height, bg_color="#070A11"):
        svg_abs = os.path.join(cwd, svg_rel_path)
        png_abs = os.path.join(cwd, png_rel_path)
        
        with open(svg_abs, "r", encoding="utf-8") as f:
            svg_content = f.read()
            
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background-color: {bg_color};
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  svg {{
    width: 100vw;
    height: 100vh;
    display: block;
  }}
</style>
</head>
<body>
{svg_content}
</body>
</html>"""
        
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name
            
        try:
            tmp_url = "file:///" + tmp_path.replace("\\", "/")
            cmd = [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--default-background-color=00000000",
                f"--window-size={width},{height}",
                f"--screenshot={png_abs}",
                tmp_url
            ]
            subprocess.run(cmd, check=True)
            print(f"[OK] Rendered {png_rel_path} ({width}x{height}, {os.path.getsize(png_abs)} bytes)")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    # 1. Logo (4K 1:1 - 3840x3840, Pure Transparent Cutout)
    render_svg("assets/sentinel_shield_logo.svg", "assets/sentinel_shield_logo.png", 3840, 3840, "transparent")

    # 2. Architecture Master Diagram (4K 13:7.2 - 3900x2160)
    render_svg("assets/architecture_diagram.svg", "assets/architecture_diagram.png", 3900, 2160, "#020408")

    # 3. Process & False-Positive Decision Diagram (4K 13:7.5 - 3900x2250)
    render_svg("assets/pfctl_decision_flow.svg", "assets/pfctl_decision_flow.png", 3900, 2250, "#020408")

    # 4. Voice SOAR & Asterisk AI Protocol Flow Diagram (4K 13:7.5 - 3900x2250)
    render_svg("assets/voice_soar_flow.svg", "assets/voice_soar_flow.png", 3900, 2250, "#03010A")

    # 5. Header Banners (High-DPI Retina Banners - 1700x152)
    headers_list = [
        "header_01_resumen",
        "header_02_arquitectura",
        "header_03_pfctl",
        "header_04_soar",
        "header_05_timeline",
        "header_06_emblema",
        "header_07_entregables",
        "header_08_despliegue",
        "header_09_equipo"
    ]
    for h in headers_list:
        render_svg(f"assets/headers/{h}.svg", f"assets/headers/{h}.png", 1700, 152, "transparent")

if __name__ == "__main__":
    convert()

