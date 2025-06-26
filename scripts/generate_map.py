import os
import json
import folium
import gpxpy

# 設定目前資料夾
folder = "2025-06"
output_file = os.path.join(folder, "index.html")
shops_file = "shops.json"

# 初始化地圖
m = folium.Map(location=[22.6273, 120.3014], zoom_start=12, control_scale=True)

# 圖層：開發路線（GPX）
staff_layer = folium.FeatureGroup(name="👟 員工開發路線", show=True)

# GPX 檔案處理
for file in sorted(os.listdir(folder)):
    if file.endswith(".gpx"):
        path = os.path.join(folder, file)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                gpx = gpxpy.parse(f)
                for track in gpx.tracks:
                    for segment in track.segments:
                        coords = [(point.latitude, point.longitude) for point in segment.points]
                        if coords:
                            geojson = folium.PolyLine(
                                coords,
                                color='blue',
                                weight=4,
                                opacity=0.8,
                                tooltip=file
                            )
                            staff_layer.add_child(geojson)
        except Exception as e:
            print(f"❌ 錯誤讀取 GPX {file}: {e}")

m.add_child(staff_layer)

# 圖層：商家位置
if os.path.exists(shops_file):
    shop_layer = folium.FeatureGroup(name="📍 開發商家", show=True)
    with open(shops_file, 'r', encoding='utf-8') as f:
        shops = json.load(f)
        for shop in shops:
            lat = shop.get("lat")
            lon = shop.get("lng")
            name = shop.get("name", "")
            note = shop.get("note", "")
            if lat and lon:
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(html='📍'),
                    tooltip=f"{name} - {note}" if note else name
                ).add_to(shop_layer)
    m.add_child(shop_layer)

# 加入圖層控制器
folium.LayerControl(collapsed=False).add_to(m)

# 輸出 HTML
m.save(output_file)
print(f"✅ 地圖已產生：{output_file}")
