import os
import json
import folium
from folium.plugins import FeatureGroupSubGroup
from pathlib import Path
import gpxpy

folder = os.environ.get("GPX_FOLDER", ".")

# 建立地圖，指定中心點與縮放
center_lat, center_lon = 22.7298662, 120.2656636
m = folium.Map(location=[center_lat, center_lon], zoom_start=15, control_scale=True)

# 商家圖層（預設紅色購物車）
shop_layer = folium.FeatureGroup(name="📍 商家地標", show=True)
m.add_child(shop_layer)

# 如果有 shops.json 就載入商家標記
shops_path = os.path.join(folder, "shops.json")
if os.path.exists(shops_path):
    with open(shops_path, "r", encoding="utf-8") as f:
        try:
            shops_json = json.load(f)
            shops_data = shops_json.get("features", [])
            for shop in shops_data:
                geometry = shop.get("geometry", {})
                properties = shop.get("properties", {})
                coords = geometry.get("coordinates", [])
                if len(coords) == 2:
                    lon, lat = coords
                    name = properties.get("name", "商家")
                    note = properties.get("note", "")
                    emoji = properties.get("emoji", "")

                    popup_html = f"""
                    <div style='font-weight:bold; font-size:14px; min-width:120px;'>{emoji} {name}</div>
                    <div style='font-size:12px; color:gray;'>{note}</div>
                    """

                    folium.Marker(
                        location=[lat, lon],
                        popup=popup_html,
                        icon=folium.Icon(color='red', icon='shopping-cart', prefix='fa')
                    ).add_to(shop_layer)
        except Exception as e:
            print("載入商家失敗:", e)

# 加入公司位置標記
folium.Marker(
    location=[22.73008, 120.331844],
    popup="🏠 公司位置",
    icon=folium.Icon(color="blue", icon="home", prefix="fa")
).add_to(m)

# 建立主圖層控制器
layer_control = folium.map.LayerControl(collapsed=False)

# 建立主圖層群組
base_group = folium.FeatureGroup(name="🚲 所有人路線", show=False)
m.add_child(base_group)

# 人名分組
person_groups = {}

# 搜尋所有 gpx 檔案
gpx_files = [f for f in os.listdir(folder) if f.endswith(".gpx")]
if not gpx_files:
    print("❗ 找不到 GPX 檔案")

for gpx_file in gpx_files:
    gpx_path = os.path.join(folder, gpx_file)
    person_name = gpx_file.split("_")[1].replace(".gpx", "") if "_" in gpx_file else "Unknown"

    if person_name not in person_groups:
        person_layer = FeatureGroupSubGroup(base_group, f"🚴 {person_name}")
        m.add_child(person_layer)
        person_groups[person_name] = person_layer
    else:
        person_layer = person_groups[person_name]

    try:
        with open(gpx_path, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)
            for track in gpx.tracks:
                for segment in track.segments:
                    coords = [(point.latitude, point.longitude) for point in segment.points]
                    folium.PolyLine(
                        coords,
                        color="blue",
                        weight=4,
                        opacity=0.8,
                        popup=gpx_file
                    ).add_to(person_layer)
    except Exception as e:
        print(f"❌ GPX 讀取失敗: {gpx_file}", e)

# 加入圖層控制器
m.add_child(layer_control)

# 加入首頁返回與標題
title_html = f"""
<div style="position: fixed; top: 10px; left: 10px; z-index: 1000;">
  <a href="../index.html" style="text-decoration: none; font-size:14px;">🔙 返回首頁</a><br>
  <div style="background:white; padding:6px 10px; border-radius:8px; font-weight:bold;">
    🦍🌍 WorldGym 分店 每日開發地圖<br>📅 月份：{folder}
  </div>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

# 輸出地圖
output_path = os.path.join(folder, "index.html")
m.save(output_path)
print(f"✅ 已產出地圖：{output_path}")
