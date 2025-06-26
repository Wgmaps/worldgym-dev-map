
import os
import json
from datetime import datetime
from pathlib import Path
import folium
from folium.plugins import MarkerCluster
import gpxpy
import gpxpy.gpx

# 找到目前目錄下所有年份-月份資料夾
root = Path(".")
folders = [f for f in root.iterdir() if f.is_dir() and f.name.startswith("2025-")]

for folder in folders:
    folder_name = folder.name
    gpx_files = list(folder.glob("*.gpx"))
    shop_file = folder / "shops.json"

    m = folium.Map(location=[22.626, 120.308], zoom_start=13, tiles="openstreetmap")

    layer_all_routes = folium.FeatureGroup(name="🧭 業務開發路線", show=True)
    for gpx_file in gpx_files:
        with open(gpx_file, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)
            for track in gpx.tracks:
                for segment in track.segments:
                    points = [(p.latitude, p.longitude) for p in segment.points]
                    folium.PolyLine(points, color="blue", weight=3).add_to(layer_all_routes)
    layer_all_routes.add_to(m)

    if shop_file.exists():
        with open(shop_file, "r", encoding="utf-8") as f:
            shops = json.load(f)
            marker_cluster = MarkerCluster(name="📍 特約商家").add_to(m)
            for shop in shops:
                location = [shop["lat"], shop["lng"]]
                popup = f"<b>{shop['name']}</b><br>{shop['address']}<br>拜訪者: {shop['sales']}"
                folium.Marker(location=location, popup=popup, icon=folium.Icon(color="red")).add_to(marker_cluster)

    folium.LayerControl(collapsed=False).add_to(m)

    output_file = folder / "index.html"
    m.save(str(output_file))
    print(f"✅ 地圖已輸出到 {output_file}")
