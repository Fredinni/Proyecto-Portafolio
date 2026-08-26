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
    
    # 1. Logo (4K 1:1 - 3840x3840)
    logo_svg = os.path.join(cwd, "assets", "sentinel_shield_logo.svg")
    logo_png = os.path.join(cwd, "assets", "sentinel_shield_logo.png")
    logo_url = "file:///" + logo_svg.replace("\\", "/")
    
    cmd_logo = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--default-background-color=00000000",
        "--window-size=3840,3840",
        f"--screenshot={logo_png}",
        logo_url
    ]
    
    # 2. Architecture Diagram (4K 24:13 - 3840x2080)
    arch_svg = os.path.join(cwd, "assets", "architecture_diagram.svg")
    arch_png = os.path.join(cwd, "assets", "architecture_diagram.png")
    arch_url = "file:///" + arch_svg.replace("\\", "/")
    
    cmd_arch = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--default-background-color=00000000",
        "--window-size=3840,2080",
        f"--screenshot={arch_png}",
        arch_url
    ]
    
    subprocess.run(cmd_logo, check=True)
    subprocess.run(cmd_arch, check=True)
    print(f"Generated {logo_png} ({os.path.getsize(logo_png)} bytes)")
    print(f"Generated {arch_png} ({os.path.getsize(arch_png)} bytes)")

if __name__ == "__main__":
    convert()
