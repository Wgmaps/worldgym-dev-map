
import os
import json
import folium
import gpxpy

folder = "2025-06"
center = [22.666, 120.316]
m = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

gpx_files = [f for f in os.listdir(folder) if f.endswith(".gpx")]
gpx_files.sort()

loaded, skipped, failed = [], [], []

for gpx_file in gpx_files:
    try:
        with open(os.path.join(folder, gpx_file), "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)

        coords = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    coords.append([point.latitude, point.longitude])

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

# 插入商家地標
try:
    with open(os.path.join(folder, "shops.json"), "r", encoding="utf-8") as f:
        shop_data = json.load(f)

    def create_popup(feature):
        name = feature["properties"].get("name", "")
        note = feature["properties"].get("note", "")
        return f"<b>📍 {name}</b><br>{note.replace('
', '<br>')}"

    shop_geojson = {
        "type": "FeatureCollection",
        "features": shop_data
    }

    shop_layer = folium.GeoJson(
        shop_geojson,
        name="📌 開發商家",
        popup=folium.GeoJsonPopup(fields=["name", "note"], aliases=["", ""])
    )
    shop_layer.add_to(m)

except Exception as e:
    print(f"❌ 錯誤處理商家地標: {e}")

# 插入圖層控制器與標題
folium.LayerControl(collapsed=False).add_to(m)

title_html = f"""
<h2 style="text-align: center; font-family: 'Noto Sans TC', sans-serif; font-size: 1.8em; margin-top: 1em;">
    🦍🌏 WorldGym NZXN 每日開發地圖 {folder} 💰
</h2>
<div style="text-align: center; margin-bottom: 1em;">
  <a href="../index.html" style="
      background-color: #f76767;
      color: white;
      padding: 0.5em 1.2em;
      text-decoration: none;
      border-radius: 10px;
      font-family: 'Noto Sans TC', sans-serif;
      font-weight: bold;
  ">🔙 返回首頁</a>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

m.save(os.path.join(folder, "index.html"))
