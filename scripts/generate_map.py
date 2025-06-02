import os
import folium
import gpxpy
import gpxpy.gpx
from datetime import datetime
import json

# 高雄座標範圍（粗略）
KAOHSIUNG_BOUNDS = {
    "min_lat": 22.4,
    "max_lat": 22.95,
    "min_lon": 120.15,
    "max_lon": 120.45
}

def is_in_kaohsiung(lat, lon):
    return (KAOHSIUNG_BOUNDS["min_lat"] <= lat <= KAOHSIUNG_BOUNDS["max_lat"] and
            KAOHSIUNG_BOUNDS["min_lon"] <= lon <= KAOHSIUNG_BOUNDS["max_lon"])

def generate_leaflet_html(gpx_files, folder):
    print(f"📍 建立地圖頁面：{folder}")
    m = folium.Map(location=[22.7279, 120.3285], zoom_start=13)  # 聚焦楠梓
    loaded = []
    skipped = []
    failed = []

    for gpx_file in gpx_files:
        coords = []
        full_path = os.path.join(folder, gpx_file)
        if not os.path.exists(full_path):
            print(f"❌ 找不到 GPX 檔案：{full_path}")
            failed.append((gpx_file, "找不到檔案"))
            continue

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                gpx = gpxpy.parse(f)

            # removed global coords initialization
            for track_seg in gpx.tracks[0].segments:
                for point in track_seg.points:
                    if is_in_kaohsiung(point.latitude, point.longitude):
                        coords.append([point.longitude, point.latitude])

            if not coords:
                skipped.append(gpx_file)
                continue

            track = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                },
                "properties": {"name": gpx_file}
            }

            folium.GeoJson(track, name=gpx_file, tooltip=gpx_file).add_to(m)
            loaded.append(gpx_file)
        except Exception as e:
            failed.append((gpx_file, str(e)))
            print(f"❌ 錯誤處理 GPX：{gpx_file} -> {e}")

    # 插入標題與回首頁按鈕
    title_html = f'''
    <h2 style="text-align: center; font-family: 'Noto Sans TC', sans-serif; font-size: 1.8em; margin-top: 1em;">
      🦍🌍 WorldGym NZXN 每日開發地圖 {folder} 💰
    </h2>
    <div style="text-align: center; margin-bottom: 1em;">
      <a href="../index.html" style="
        background-color: #ff7675;
        color: white;
        padding: 0.5em 1.2em;
        text-decoration: none;
        border-radius: 10px;
        font-family: 'Noto Sans TC', sans-serif;
        font-weight: bold;
      ">⬅️ 返回首頁</a>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    m.get_root().html.add_child(folium.Element('''<link rel="stylesheet" href="https://unpkg.com/leaflet-control-search@2.9.8/dist/leaflet-search.min.css" />'''))
    m.get_root().html.add_child(folium.Element('''
<!-- 插入商家搜尋功能與圖層控制器 -->
<link rel="stylesheet" href="https://unpkg.com/leaflet-control-search@2.9.8/dist/leaflet-search.min.css" />
<script src="https://unpkg.com/leaflet-control-search@2.9.8/dist/leaflet-search.min.js"></script>
<script>
setTimeout(() => {
  const mapObj = window.map || map_a18041249b458e44a073500f354e3cfc;
  const layer_control = L.control.layers({}, {}, { collapsed: false }).addTo(mapObj);

  fetch("shops.json")
    .then(res => res.json())
    .then(data => {
      const shopLayer = L.geoJSON(data, {
        onEachFeature: function (feature, layer) {
          const name = feature.properties.name || "未知地點";
          const note = feature.properties.note || "";
          const emoji = feature.properties.emoji || "📌";
          const popup = `<b>${emoji} ${name}</b><br>${note.replaceAll("
", "<br>")}`;
          layer.bindPopup(popup);
          layer.feature = { properties: { name } };
        }
      }).addTo(mapObj);

      layer_control.addOverlay(shopLayer, "🏪 開發商家");

      const searchControl = new L.Control.Search({
        layer: shopLayer,
        propertyName: 'name',
        marker: false,
        collapsed: false,
        moveToLocation: function(latlng, title, map) {
          map.setView(latlng, 17);
        }
      });
      mapObj.addControl(searchControl);
    });
}, 500);
</script>
'''))

    # 顯示 GPX 載入狀態
    html = m.get_root().render()
    html += "<div style='padding:1em;font-family:sans-serif'>"
    if loaded:
        html += "<h3>✅ 載入成功的 GPX：</h3><ul>"
        for f in loaded:
            html += f"<li>{f}</li>"
        html += "</ul>"
    if skipped:
        html += "<h3>⚠️ 未包含高雄區域的 GPX（已略過）：</h3><ul>"
        for f in skipped:
            html += f"<li>{f}</li>"
        html += "</ul>"
    if failed:
        html += "<h3>❌ 載入失敗的 GPX：</h3><ul>"
        for f, err in failed:
            html += f"<li>{f}<br><code>{err}</code></li>"
        html += "</ul>"
    html += "</div>"
    return html

def update_home_index(months):
    html = "<h1>🌍🦍 WorldGym 地圖首頁💰</h1><ul>"
    for m in sorted(months):
        html += f'<li><a href="{m}/index.html">{m}</a></li>'
    html += "</ul>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    folders = [f for f in os.listdir() if os.path.isdir(f) and f.startswith("2025-")]
    generated = []
    for folder in folders:
        print(f"📂 處理資料夾：{folder}")
        gpx_files = [f for f in os.listdir(folder) if f.endswith(".gpx")]
        print(f"🔍 發現 GPX 檔案：{gpx_files}")
        if not gpx_files:
            print(f"⚠️ {folder} 中沒有找到 GPX")
            continue
        html = generate_leaflet_html(gpx_files, folder)
        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        generated.append(folder)

    update_home_index(generated)
    print("✅ 所有 index.html 重新產生完成")

if __name__ == "__main__":
    main()
