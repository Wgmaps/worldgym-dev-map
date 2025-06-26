
import os
import json
import folium
import gpxpy

# 地圖初始化
m = folium.Map(location=[22.6273, 120.3014], zoom_start=12, control_scale=True)

gpx_folder = '2025-06'
gpx_files = [f for f in os.listdir(gpx_folder) if f.endswith('.gpx')]

# GPX 路線圖層群組
track_group = folium.FeatureGroup(name='🚴‍♂️員工開發路線', show=True)

for gpx_file in sorted(gpx_files):
    file_path = os.path.join(gpx_folder, gpx_file)
    with open(file_path, 'r') as f:
        gpx = gpxpy.parse(f)
    for track in gpx.tracks:
        for segment in track.segments:
            coords = [(point.latitude, point.longitude) for point in segment.points]
            if coords:
                folium.PolyLine(coords, color='blue', weight=4.5, opacity=0.8, tooltip=gpx_file).add_to(track_group)

track_group.add_to(m)

# 商家地標圖層
try:
    with open(os.path.join(gpx_folder, 'shops.json'), 'r', encoding='utf-8') as f:
        shop_data = json.load(f)

    shop_group = folium.FeatureGroup(name='📍開發商家', show=True)
    for feature in shop_data['features']:
        props = feature['properties']
        lat, lon = feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0]
        name = props.get('name', '未命名')
        note = props.get('note', '')
        emoji = props.get('emoji', '📍')
        popup = folium.Popup(f"<b>{emoji} {name}</b><br>{note}", max_width=300)
        folium.Marker(location=[lat, lon], popup=popup, icon=folium.Icon(color='red', icon='info-sign')).add_to(shop_group)
    shop_group.add_to(m)
except Exception as e:
    print(f"⚠️ 無法載入商家資料: {e}")

# 控制器加入地圖
folium.LayerControl(collapsed=False).add_to(m)
m.save(os.path.join(gpx_folder, 'index.html'))


# 新增首頁 index.html
def generate_homepage():
    folders = sorted([f for f in os.listdir() if os.path.isdir(f) and f.startswith("2025-")])
    html = "<h1>🌍🦍 WorldGym 地圖首頁💰</h1><ul>"
    for folder in folders:
        html += f'<li><a href="{folder}/index.html">{folder}</a></li>'
    html += "</ul>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

generate_homepage()
