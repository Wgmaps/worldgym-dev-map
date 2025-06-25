
import os
import json
import gpxpy
import folium

# GPX 路徑與輸出地圖資料夾
folder = "2025-06"
output_file = os.path.join(folder, "index.html")
gpx_files = [f for f in os.listdir(folder) if f.endswith(".gpx")]

# 初始化地圖（高雄市中心）
m = folium.Map(location=[22.6273, 120.3014], zoom_start=13, tiles="OpenStreetMap")

# GPX 路線圖層群組
route_group = folium.FeatureGroup(name="🛣️ 開發路線")

for gpx_file in gpx_files:
    path = os.path.join(folder, gpx_file)
    with open(path, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)
        for track in gpx.tracks:
            for segment in track.segments:
                coords = [(point.latitude, point.longitude) for point in segment.points]
                folium.PolyLine(coords, color="blue", weight=4, opacity=0.8, tooltip=gpx_file).add_to(route_group)

route_group.add_to(m)

# 商家圖層 FeatureGroup
shop_layer = folium.FeatureGroup(name="📍 開發商家")

shops_path = os.path.join(folder, "shops.json")
if os.path.exists(shops_path):
    with open(shops_path, "r", encoding="utf-8") as f:
        shops = json.load(f)
        for shop in shops["features"]:
            props = shop["properties"]
            coords = shop["geometry"]["coordinates"]
            name = props.get("name", "")
            note = props.get("note", "")
            emoji = props.get("emoji", "📍")
            popup_html = f"<b>{emoji} {name}</b><br>{note.replace('
', '<br>')}"
            folium.Marker(
                location=[coords[1], coords[0]],
                popup=popup_html,
                tooltip=name,
                icon=folium.DivIcon(html=f"<div style='font-size:18px;'>{emoji}</div>")
            ).add_to(shop_layer)

shop_layer.add_to(m)

# 加入圖層控制器
folium.LayerControl(collapsed=False).add_to(m)

# 自訂標題
title_html = f'''
<h2 style="text-align: center; font-family: 'Noto Sans TC'; margin-top: 1em;">
  🦍🌏 WorldGym NZXN 每日開發地圖 {folder} 💰
</h2>
<div style="text-align: center; margin-bottom: 1em;">
  <a href="../index.html" style="background-color: #f76775; color: white; padding: 0.5em 1.2em; text-decoration: none; border-radius: 10px; font-weight: bold;">
    ⬅️ 返回首頁
  </a>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

# 輸出地圖
m.save(output_file)
print(f"✅ 地圖已儲存至 {output_file}")
