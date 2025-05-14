
import os
import subprocess

def generate_leaflet_html(gpx_files, folder):
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>WorldGym 每日開發路線圖 - {folder}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://unpkg.com/togeojson@0.16.0"></script>
</head>
<body>
  <h2 style="font-family: sans-serif; text-align: center;">WorldGym 每日開發路線圖 - {folder}</h2>
  <div id="map" style="width: 100%; height: 90vh;"></div>
  <script>
    var map = L.map('map').setView([25.0330, 121.5654], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {{
      maxZoom: 18
    }}).addTo(map);
"""

    for gpx in gpx_files:
        html += f"""
    fetch('{gpx}')
      .then(res => res.text())
      .then(str => (new window.DOMParser()).parseFromString(str, "text/xml"))
      .then(data => {{
        var track = togeojson.gpx(data);
        L.geoJSON(track, {{
          style: {{ color: '#f00', weight: 3 }}
        }}).bindPopup('{gpx}').addTo(map);
      }});
"""

    html += """
  </script>
</body>
</html>
"""
    return html

def update_home_index(months):
    html = "<h1>WorldGym 地圖首頁</h1><ul>"
    for m in sorted(months):
        html += f'<li><a href="{m}/index.html">{m}</a></li>'
    html += "</ul>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    folders = [f for f in os.listdir() if os.path.isdir(f) and f.startswith("2025-")]
    generated = []
    for folder in folders:
        gpx_files = [f for f in os.listdir(folder) if f.endswith(".gpx")]
        if not gpx_files:
            continue
        html = generate_leaflet_html(gpx_files, folder)
        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        generated.append(folder)
        print(f"✅ {folder}/index.html 產生完成")

    update_home_index(generated)
    print("🏠 首頁 index.html 已更新完成")

    subprocess.run(["git", "config", "--global", "user.email", "mapbot@worldgym.com"])
    subprocess.run(["git", "config", "--global", "user.name", "mapbot"])
    subprocess.run(["git", "add", "index.html"])
    subprocess.run(["git", "commit", "-m", "auto: 更新首頁 index.html"])
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    main()
