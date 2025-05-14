
import os

def generate_leaflet_html(gpx_files):
    html = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>WorldGym 每日開發路線圖</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://unpkg.com/togeojson@0.16.0"></script>
</head>
<body>
  <h2 style="font-family: sans-serif; text-align: center;">WorldGym 每日開發路線圖</h2>
  <div id="map" style="width: 100%; height: 90vh;"></div>
  <script>
    var map = L.map('map').setView([25.0330, 121.5654], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
    }).addTo(map);
  '''

    for gpx in gpx_files:
        html += f'''
    fetch('{gpx}')
      .then(res => res.text())
      .then(str => (new window.DOMParser()).parseFromString(str, "text/xml"))
      .then(data => {{
        var track = togeojson.gpx(data);
        L.geoJSON(track, {{
          style: {{ color: '#f00', weight: 3 }}
        }}).bindPopup("{gpx}").addTo(map);
      }});
        '''

    html += '''
  </script>
</body>
</html>
    '''
    return html

def main():
    folder = "2025-05"
    gpx_files = [f for f in os.listdir(folder) if f.endswith(".gpx")]
    if not gpx_files:
        print("⚠️ 找不到任何 GPX 檔案，停止產出。")
        return

    html = generate_leaflet_html(gpx_files)
    with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ 已成功產出地圖：index.html")

if __name__ == "__main__":
    main()
