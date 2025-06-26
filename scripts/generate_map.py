
from pathlib import Path
import json
import gpxpy
import folium

# 地圖初始化（中心座標設為高雄）
m = folium.Map(location=[22.6273, 120.3014], zoom_start=12)

# ---------- 商家圖層 ----------
shops_file = Path("shops.json")
if shops_file.exists():
    with open(shops_file, "r", encoding="utf-8") as f:
        shops = json.load(f)
    shop_layer = folium.FeatureGroup(name="📍 商家地標", show=True)
    for shop in shops:
        name = shop.get("name", "無名稱")
        note = shop.get("note", "")
        lat = shop.get("lat")
        lon = shop.get("lon")
        if lat and lon:
            folium.Marker(
                location=[lat, lon],
                popup=f"{name}<br>{note}",
                tooltip=name,
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(shop_layer)
    shop_layer.add_to(m)

# ---------- GPX 路線圖層 ----------
gpx_dir = Path(".")
gpx_files = list(gpx_dir.glob("*.gpx"))
gpx_layer = folium.FeatureGroup(name="🛤️ 開發路線", show=True)

for gpx_file in gpx_files:
    try:
        with open(gpx_file, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)
        for track in gpx.tracks:
            for segment in track.segments:
                coords = [(point.latitude, point.longitude) for point in segment.points]
                folium.PolyLine(
                    locations=coords,
                    color="blue",
                    weight=3,
                    opacity=0.7,
                    popup=str(gpx_file.name),
                ).add_to(gpx_layer)
    except Exception as e:
        print(f"❌ 無法載入 {gpx_file.name}: {e}")

gpx_layer.add_to(m)

# ---------- 控制器 ----------
folium.LayerControl(collapsed=False).add_to(m)

# ---------- 輸出 HTML ----------
m.save("index.html")
