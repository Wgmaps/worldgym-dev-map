
import os
import re
import folium
import gpxpy
import json

folders = sorted([f for f in os.listdir() if os.path.isdir(f) and f.startswith("2025-")])

def extract_name(filename):
    name_part = re.sub(r'^\d{4}_', '', filename)
    name_part = re.sub(r'\d*(?=\.gpx$)', '', name_part)
    name_part = name_part.replace('.gpx', '')
    return name_part

def generate_map_for_folder(gpx_folder):
    print(f"📍 處理資料夾：{gpx_folder}")
    m = folium.Map(location=[22.7283, 120.3273], zoom_start=15, control_scale=True)

    title_html = f'''
         <h3 align="center" style="font-size:24px">
         🦍🌍 WorldGym NZXN 每日開發地圖 {gpx_folder} 💰
         </h3>
         <div style="text-align:center;margin-bottom:10px;">
         <a href="../index.html"><button style="background-color:red;color:white;border:none;padding:5px 10px;border-radius:5px;">返回首頁</button></a>
         </div>
     '''
    m.get_root().html.add_child(folium.Element(title_html))

    m.get_root().html.add_child(folium.Element("""
    <script>
    function searchShop() {
        const input = document.getElementById('shopSearch').value.trim();
        if (!input) return;
        let found = false;
        for (let i in window.shopMarkers) {
            const marker = window.shopMarkers[i];
            const name = marker.getPopup().getContent();
            if (name.includes(input)) {
                marker.openPopup();
                window.map.setView(marker.getLatLng(), 18);
                found = true;
                break;
            }
        }
        if (!found) {
            alert("找不到商家：" + input);
        }
    }
    </script>
    <div style='position: fixed; top: 10px; right: 50px; z-index: 9999; background: white; padding: 5px 10px; border-radius: 8px; box-shadow: 0 0 5px rgba(0,0,0,0.2);'>
      <input type='text' id='shopSearch' placeholder='搜尋商家名稱...' style='width:160px;' onkeydown='if(event.key===\"Enter\")searchShop()'>
      <button onclick='searchShop()'>搜尋</button>
    </div>
    """))

    merchant_layer = folium.FeatureGroup(name='🏪 特約商家')
    m.add_child(merchant_layer)

    shops_file = os.path.join(gpx_folder, 'shops.json')
    if os.path.exists(shops_file):
        with open(shops_file, 'r', encoding='utf-8') as f:
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

                        popup_html = f"""<div style='font-size:14px; line-height:1.4; white-space:nowrap;'>📍 {name}<br>{note}</div>"""

                        folium.Marker(
                            location=[lat, lon],
                            popup=popup
                        # 用來收集 marker JS 物件
                        # shopMarkers will be handled in custom HTML_html,
                            icon=folium.Icon(color='red', icon='shopping-cart', prefix='fa')
                        ).add_to(merchant_layer)

            except Exception as e:
                print(f"❌ 無法讀取商家地標: {e}")

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
