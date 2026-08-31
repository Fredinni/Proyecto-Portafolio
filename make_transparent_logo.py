#!/usr/bin/env python3
import os
import subprocess
import tempfile
from PIL import Image

edge_paths = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
]
browser = next((p for p in edge_paths if os.path.exists(p)), None)

with open("assets/sentinel_shield_logo.svg", "r", encoding="utf-8") as f:
    svg_content = f.read()

# Render against a distinct chroma key color #00FF00 (Pure Green)
html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ background: #00FF00 !important; width: 100vw; height: 100vh; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
svg {{ width: 92vw; height: 92vh; }}
</style>
</head><body>{svg_content}</body></html>"""

with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
    tmp.write(html)
    tmp_path = tmp.name

cwd = os.path.abspath(".")
raw_png = os.path.join(cwd, "assets/temp_shield_raw.png")
out_png = os.path.join(cwd, "assets/sentinel_shield_logo.png")

try:
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1600,1600",
        f"--screenshot={raw_png}",
        "file:///" + tmp_path.replace("\\", "/")
    ]
    subprocess.run(cmd, check=True)
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

# Process with PIL to extract pure alpha transparency from chroma key
img = Image.open(raw_png).convert("RGBA")
datas = img.getdata()

new_data = []
for item in datas:
    # item is (r, g, b, a)
    r, g, b, a = item
    # If pixel is chroma green (#00FF00 or close green threshold)
    if g > 210 and r < 60 and b < 60:
        new_data.append((0, 0, 0, 0))  # 100% Transparent!
    elif g > 150 and r < 80 and b < 80:
        # Soft antialiased edge
        alpha = int(255 * (1 - (g - r) / 255.0))
        new_data.append((r, min(g, 60), b, max(0, min(255, alpha))))
    else:
        new_data.append(item)

img.putdata(new_data)
img.save(out_png, "PNG")
print(f"[OK] Successfully created transparent logo: {out_png}")

if os.path.exists(raw_png):
    os.remove(raw_png)

# Verify
res = Image.open(out_png)
print(f"Result Mode: {res.mode}, Size: {res.size}")
corner = res.getpixel((10, 10))
print(f"Corner Pixel (10, 10): {corner} (Alpha={corner[3]})")
center = res.getpixel((800, 800))
print(f"Center Pixel (800, 800): {center} (Alpha={center[3]})")
