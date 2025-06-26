import os
import json
import folium
from pathlib import Path

year_month_dirs = sorted([
    d for d in os.listdir(".")
    if os.path.isdir(d) and d.startswith("2025-")
])

index_html = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8" />
    <title>WorldGym NZXN 每日開發地圖</title>
    <style>
        body { font-family: 'Noto Sans TC', sans-serif; text-align: center; background: #f5f5f5; }
        h1 { margin-top: 40px; }
        .container { display: flex; flex-wrap: wrap; justify-content: center; margin: 40px auto; max-width: 1000px; }
        .card {
            background: white; padding: 20px; margin: 10px; border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 200px; text-align: center;
        }
        a { text-decoration: none; color: #333; font-weight: bold; }
    </style>
</head>
<body>
    <h1>📍 WorldGym NZXN 每月開發地圖 📍</h1>
    <div class="container">
"""

for folder in year_month_dirs:
    folder_path = Path(folder)
    gpx_files = list(folder_path.glob("*.gpx"))
    if gpx_files:
        index_html += f'<div class="card"><a href="{folder}/index.html">{folder}</a></div>\n'

index_html += """
    </div>
    <p style="margin-top: 50px; color: #777;">更新時間：自動同步 GitHub</p>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_html)

# 處理每個月資料夾
for folder in year_month_dirs:
    gpx_files = sorted([
        f for f in os.listdir(folder)
        if f.endswith(".gpx")
    ])
    if not gpx_files:
        continue

    m = folium.Map(location=[22.6268, 120.3089], zoom_start=13, tiles="openstreetmap")
    feature_group = folium.FeatureGroup(name="員工開發路線", show=True)
    for gpx in gpx_files:
        gpx_path = os.path.join(folder, gpx)
        try:
            import gpxpy
            with open(gpx_path, "r") as f:
                gpx_obj = gpxpy.parse(f)
                for track in gpx_obj.tracks:
                    for segment in track.segments:
                        coords = [(p.latitude, p.longitude) for p in segment.points]
                        folium.PolyLine(coords, color="blue", weight=4, opacity=0.7,
                                        tooltip=gpx).add_to(feature_group)
        except Exception as e:
            print(f"Error loading {gpx}: {e}")
    feature_group.add_to(m)

    # 商家圖層
    shops_path = os.path.join(folder, "shops.json")
    if os.path.exists(shops_path):
        with open(shops_path, "r", encoding="utf-8") as f:
            shops = json.load(f)

        shop_layer = folium.FeatureGroup(name="商家地標", show=True)
        for shop in shops:
            folium.Marker(
                location=[shop["lat"], shop["lng"]],
                popup=f'📍 {shop["name"]} ({shop["note"]})',
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(shop_layer)
        shop_layer.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    m.save(os.path.join(folder, "index.html"))
