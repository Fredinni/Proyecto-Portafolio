import os
import subprocess

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
    
    # 1. Logo
    logo_svg = os.path.join(cwd, "assets", "sentinel_shield_logo.svg")
    logo_png = os.path.join(cwd, "assets", "sentinel_shield_logo.png")
    logo_url = "file:///" + logo_svg.replace("\\", "/")
    
    cmd_logo = [
        browser,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=800,800",
        f"--screenshot={logo_png}",
        logo_url
    ]
    
    # 2. Architecture Diagram
    arch_svg = os.path.join(cwd, "assets", "architecture_diagram.svg")
    arch_png = os.path.join(cwd, "assets", "architecture_diagram.png")
    arch_url = "file:///" + arch_svg.replace("\\", "/")
    
    cmd_arch = [
        browser,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1200,650",
        f"--screenshot={arch_png}",
        arch_url
    ]
    
    subprocess.run(cmd_logo, check=True)
    subprocess.run(cmd_arch, check=True)
    print(f"Generated {logo_png} ({os.path.getsize(logo_png)} bytes)")
    print(f"Generated {arch_png} ({os.path.getsize(arch_png)} bytes)")

if __name__ == "__main__":
    convert()
