
import os
import json
from pathlib import Path
import folium
from folium.plugins import MarkerCluster
from gpxpy import parse as parse_gpx

# 自動取得目前資料夾名稱作為地圖標題
root = Path(".")
current_folder = next(p for p in root.iterdir() if p.is_dir() and p.name.startswith("2025-"))
year_month = current_folder.name

# 建立地圖
m = folium.Map(location=[22.63, 120.3], zoom_start=13, control_scale=True)

# 加入圖層控制
gpx_layer = folium.FeatureGroup(name="📍員工開發路線", show=True)
m.add_child(gpx_layer)

# GPX 檔案處理
for gpx_file in sorted(current_folder.glob("*.gpx")):
    with open(gpx_file, "r", encoding="utf-8") as f:
        gpx = parse_gpx(f.read())
        for track in gpx.tracks:
            for segment in track.segments:
                points = [[p.latitude, p.longitude] for p in segment.points]
                folium.PolyLine(points, color="blue", weight=4).add_to(gpx_layer)

# 商家地標
shops_path = current_folder / "shops.json"
if shops_path.exists():
    with open(shops_path, "r", encoding="utf-8") as f:
        shops = json.load(f)
    shop_layer = folium.FeatureGroup(name="🏪 商家地標", show=True)
    for shop in shops:
        if isinstance(shop, dict):
            location = [shop["lat"], shop["lng"]]
            name = shop.get("name", "")
            note = shop.get("note", "")
            folium.Marker(
                location,
                icon=folium.DivIcon(html=f"<div style='font-size: 24px;'>📍</div>"),
                tooltip=f"{name} ({note})"
            ).add_to(shop_layer)
    m.add_child(shop_layer)

# 圖層控制器
folium.LayerControl(position="topright").add_to(m)

# 匯出地圖 HTML
output_path = current_folder / "index.html"
m.save(str(output_path))
print(f"✔ 地圖已輸出到 {output_path}")
