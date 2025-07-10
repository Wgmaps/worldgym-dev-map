
import os
import re
import folium
import gpxpy
import json

# 自動處理所有月份資料夾
folders = sorted([f for f in os.listdir() if os.path.isdir(f) and f.startswith("2025-")])

def extract_name(filename):
    name_part = re.sub(r'^\d{4}_', '', filename)         # 移除日期
    name_part = re.sub(r'\d*(?=\.gpx$)', '', name_part)  # 移除名字後的數字
    name_part = name_part.replace('.gpx', '')
    return name_part

def generate_map_for_folder(gpx_folder):
    print(f"📍 處理資料夾：{gpx_folder}")
    m = folium.Map(location=[22.6273, 120.3014], zoom_start=13, control_scale=True)

    # 返回首頁按鈕
    title_html = f'''
         <h3 align="center" style="font-size:24px">
         🦍🌍 WorldGym NZXN 每日開發地圖 {gpx_folder} 💰
         </h3>
         <div style="text-align:center;margin-bottom:10px;">
         <a href="../index.html"><button style="background-color:red;color:white;border:none;padding:5px 10px;border-radius:5px;">返回首頁</button></a>
         </div>
     '''
    m.get_root().html.add_child(folium.Element(title_html))

    # 特約商家圖層
    merchant_layer = folium.FeatureGroup(name='🏪 特約商家')
    m.add_child(merchant_layer)

    # 嘗試載入 shops.json
    shops_file = os.path.join(gpx_folder, 'shops.json')
    if os.path.exists(shops_file):
        with open(shops_file, 'r', encoding='utf-8') as f:
            shops_data = json.load(f)
            for shop in shops_data:
                lat = shop.get('lat')
                lon = shop.get('lon')
                name = shop.get('name', '商家')
                folium.Marker(
                    location=[lat, lon],
                    popup=name,
                    icon=folium.Icon(color='red', icon='shopping-cart', prefix='fa')
                ).add_to(merchant_layer)

    # 分業務路線
    gpx_files = [f for f in os.listdir(gpx_folder) if f.endswith('.gpx')]
    agent_layers = {}

    for gpx_file in sorted(gpx_files):
        name = extract_name(gpx_file)
        if name not in agent_layers:
            agent_layers[name] = folium.FeatureGroup(name=f'🚴 {name}')
            m.add_child(agent_layers[name])

        file_path = os.path.join(gpx_folder, gpx_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as gpx_file_content:
                gpx = gpxpy.parse(gpx_file_content)
                for track in gpx.tracks:
                    for segment in track.segments:
                        points = [(point.latitude, point.longitude) for point in segment.points]
                        folium.PolyLine(points, color="blue", weight=4, opacity=0.8).add_to(agent_layers[name])
        except Exception as e:
            print(f"❌ 無法處理 {gpx_file}: {e}")

    folium.LayerControl(collapsed=False).add_to(m)

    output_file = os.path.join(gpx_folder, "index.html")
    m.save(output_file)
    print(f"✅ 已產生：{output_file}")

for folder in folders:
    generate_map_for_folder(folder)
