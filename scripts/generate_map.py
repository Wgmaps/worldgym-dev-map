
import os
import json
import folium
from folium.plugins import MarkerCluster
from pathlib import Path

root = Path(".")
output_map_filename = "index.html"

# 取得所有月份資料夾
month_dirs = sorted([f.name for f in root.iterdir() if f.is_dir() and f.name.startswith("2025-")])

for month in month_dirs:
    folder = root / month
    gpx_files = [f for f in os.listdir(folder) if f.endswith(".gpx")]
    shop_file = folder / "shops.json"
    map_center = [22.6273, 120.3014]  # 高雄市中心

    m = folium.Map(location=map_center, zoom_start=13, control_scale=True)

    # GPX 圖層群組
    if gpx_files:
        gpx_group = folium.FeatureGroup(name="📍員工開發路線", show=True)
        for gpx_file in gpx_files:
            try:
                import gpxpy
                with open(folder / gpx_file, "r", encoding="utf-8") as f:
                    gpx = gpxpy.parse(f)
                    for track in gpx.tracks:
                        for segment in track.segments:
                            points = [(point.latitude, point.longitude) for point in segment.points]
                            folium.PolyLine(points, color="blue", weight=4, opacity=0.6,
                                            tooltip=gpx_file).add_to(gpx_group)
            except Exception as e:
                print(f"❌ GPX 解析失敗: {gpx_file} -> {e}")
        gpx_group.add_to(m)

    # 商家地標圖層
    if shop_file.exists():
        with open(shop_file, "r", encoding="utf-8") as f:
            shops = json.load(f)
        shop_group = folium.FeatureGroup(name="🏪 商家地標", show=True)
        marker_cluster = MarkerCluster().add_to(shop_group)
        for shop in shops:
            folium.Marker(
                location=[shop["lat"], shop["lng"]],
                popup=folium.Popup(f"{shop['name']}<br>{shop.get('note', '')}", max_width=300),
                icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
            ).add_to(marker_cluster)
        shop_group.add_to(m)

    # 圖層控制器
    folium.LayerControl(collapsed=False).add_to(m)

    # 輸出 index.html
    m.save(str(folder / output_map_filename))
    print(f"✅ 成功產生：{folder / output_map_filename}")
