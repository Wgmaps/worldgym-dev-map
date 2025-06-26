
import os
import folium
import gpxpy
import json

gpx_folder = '2025-06'
shops_file = 'shops.json'

map_center = [22.65, 120.3]
m = folium.Map(location=map_center, zoom_start=13, tiles='openstreetmap')

# 所有 GPX 圖層與 FeatureGroup（用於控制器）
gpx_layer_group = folium.FeatureGroup(name="所有 GPX 路線", show=True)
employee_layer_group = folium.FeatureGroup(name="👟 員工開發路線", show=True)

loaded_files = []
skipped_files = []
failed_files = []

for filename in os.listdir(gpx_folder):
    if not filename.endswith('.gpx'):
        continue
    filepath = os.path.join(gpx_folder, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        coords = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    coords.append((point.latitude, point.longitude))

        if not coords:
            skipped_files.append(filename)
            continue

        layer = folium.PolyLine(locations=coords, color='blue', weight=3, opacity=0.8)
        layer.add_to(gpx_layer_group)

        if 'ben' in filename.lower():
            # 員工開發路線的判斷依照檔名含 ben
            layer.add_to(employee_layer_group)

        loaded_files.append(filename)
    except Exception as e:
        failed_files.append((filename, str(e)))

# 加入 GPX 圖層群組到地圖
gpx_layer_group.add_to(m)
employee_layer_group.add_to(m)

# 加入商家地標（shops.json）
try:
    with open(shops_file, 'r', encoding='utf-8') as f:
        shop_data = json.load(f)

    shop_group = folium.FeatureGroup(name="📍 商家地標", show=True)

    for feature in shop_data["features"]:
        prop = feature["properties"]
        coords = feature["geometry"]["coordinates"]
        name = prop.get("name", "商家")
        note = prop.get("note", "")
        popup = f"{name}<br>{note}" if note else name
        folium.Marker(
            location=[coords[1], coords[0]],
            icon=folium.DivIcon(html='<div style="font-size:20px;">📍</div>'),
            popup=popup
        ).add_to(shop_group)

    shop_group.add_to(m)
except Exception as e:
    print(f"❌ 無法載入 shops.json：{e}")

# 加入圖層控制器
folium.LayerControl(collapsed=False).add_to(m)

# 儲存
m.save(os.path.join(gpx_folder, 'index.html'))
print("✅ 地圖已更新，共載入 GPX：", len(loaded_files), "略過：", len(skipped_files), "錯誤：", len(failed_files))
