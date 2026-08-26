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
                f"--window-size={width},{height}",
                f"--screenshot={png_abs}",
                tmp_url
            ]
            subprocess.run(cmd, check=True)
            print(f"[OK] Rendered {png_rel_path} ({width}x{height}, {os.path.getsize(png_abs)} bytes)")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    # 1. Logo (4K 1:1 - 3840x3840)
    render_svg("assets/sentinel_shield_logo.svg", "assets/sentinel_shield_logo.png", 3840, 3840, "#070A11")

    # 2. Architecture Diagram (4K 24:13 - 3840x2080)
    render_svg("assets/architecture_diagram.svg", "assets/architecture_diagram.png", 3840, 2080, "#070A11")

if __name__ == "__main__":
    convert()

