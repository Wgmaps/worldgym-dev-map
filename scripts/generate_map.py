
import os
import json
import folium
import gpxpy

def generate_map(folder):
    m = folium.Map(location=[22.666, 120.316], zoom_start=13, control_scale=True)

    gpx_files = sorted([f for f in os.listdir(folder) if f.endswith(".gpx")])
    for filename in gpx_files:
        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)
            for track in gpx.tracks:
                for segment in track.segments:
                    coords = [(pt.latitude, pt.longitude) for pt in segment.points]
                    if coords:
                        folium.PolyLine(coords, tooltip=filename, color="blue").add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    m.save(os.path.join(folder, "index.html"))

    # 插入商家控制器 script
    html_path = os.path.join(folder, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    script_block = """
<script>
setTimeout(() => {
  const mapObj = window.map || map_a10841249b45be44a073580f354e3cfc;
  const layerControl = L.control.layers({}, {}, { collapsed: false }).addTo(mapObj);
  fetch('shops.json')
    .then(res => res.json())
    .then(data => {
      const shopLayer = L.geoJSON(data, {
        onEachFeature: function (feature, layer) {
          const name = feature.properties.name || "未命名商家";
          const note = feature.properties.note || "";
          const emoji = feature.properties.emoji || "📍";
          const popup = `<b>${emoji} ${name}</b><br>${note.replaceAll("\n", "<br>")}`;
          layer.bindPopup(popup);
        },
        pointToLayer: function (feature, latlng) {
          return L.marker(latlng);
        }
      }).addTo(mapObj);
      layerControl.addOverlay(shopLayer, "📍 開發商家");
    });
}, 0);
</script>
</body>
"""

    html = html.replace("</body>", script_block)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ 已產生地圖與商家圖層控制器：{html_path}")

if __name__ == "__main__":
    generate_map("2025-06")
