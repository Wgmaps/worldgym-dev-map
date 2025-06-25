
import os
import json
import gpxpy
import folium

def generate_map(folder):
    m = folium.Map(location=[22.65, 120.3], zoom_start=13, control_scale=True)
    layer_control = folium.LayerControl(collapsed=False)

    # 加入所有 GPX 路線
    gpx_files = sorted([f for f in os.listdir(folder) if f.endswith(".gpx")])
    for filename in gpx_files:
        filepath = os.path.join(folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)
            for track in gpx.tracks:
                for segment in track.segments:
                    coords = [(point.latitude, point.longitude) for point in segment.points]
                    if coords:
                        folium.PolyLine(coords, tooltip=filename, color="blue").add_to(m)

    # 加入圖層控制器
    layer_control.add_to(m)

    # 儲存地圖 HTML
    output_path = os.path.join(folder, "index.html")
    m.save(output_path)

    # 插入商家控制器 JS
    with open(output_path, "r", encoding="utf-8") as f:
        html = f.read()

    insert_script = """
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
        })
        .catch(error => {
          console.error("載入商家圖層失敗：", error);
        });
    }, 0);
    </script>
    </body>
    """

    html = html.replace("</body>", insert_script)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ 成功產生地圖：{output_path}")

# 你可以手動呼叫 generate_map("2025-06")
if __name__ == "__main__":
    generate_map("2025-06")
