
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
    html = "<h1>🌍 WorldGym 地圖首頁</h1><ul>"
    for folder in folders:
        html += f'<li><a href="{folder}/index.html">{folder}</a></li>'
    html += "</ul>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
# 高雄座標範圍（粗略）
KAOHSIUNG_BOUNDS = {
    "min_lat": 22.4,
    "max_lat": 22.95,
    "min_lon": 120.15,
    "max_lon": 120.45
}

def is_in_kaohsiung(lat, lon):
    return (KAOHSIUNG_BOUNDS["min_lat"] <= lat <= KAOHSIUNG_BOUNDS["max_lat"] and
            KAOHSIUNG_BOUNDS["min_lon"] <= lon <= KAOHSIUNG_BOUNDS["max_lon"])

def generate_leaflet_html(gpx_files, folder):
    print(f"📍 建立地圖頁面：{folder}")
    m = folium.Map(location=[22.7279, 120.3285], zoom_start=13)  # 聚焦楠梓
    loaded = []
    skipped = []
    failed = []

    for gpx_file in gpx_files:
        full_path = os.path.join(folder, gpx_file)
        if not os.path.exists(full_path):
            print(f"❌ 找不到 GPX 檔案：{full_path}")
            failed.append((gpx_file, "找不到檔案"))
            continue

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                gpx = gpxpy.parse(f)

            coords = []
            for track_seg in gpx.tracks[0].segments:
                for point in track_seg.points:
                    if is_in_kaohsiung(point.latitude, point.longitude):
                        coords.append([point.longitude, point.latitude])

            if not coords:
                skipped.append(gpx_file)
                continue

            track = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                },
                "properties": {"name": gpx_file}
            }

            folium.GeoJson(track, name=gpx_file, tooltip=gpx_file).add_to(m)
            loaded.append(gpx_file)
        except Exception as e:
            failed.append((gpx_file, str(e)))
            print(f"❌ 錯誤處理 GPX：{gpx_file} -> {e}")

    # 插入標題與回首頁按鈕
    title_html = f'''
    <h2 style="text-align: center; font-family: 'Noto Sans TC', sans-serif; font-size: 1.8em; margin-top: 1em;">
      🦍🌍 WorldGym NZXN 每日開發地圖 {folder} 💰
    </h2>
    <div style="text-align: center; margin-bottom: 1em;">
      <a href="../index.html" style="
        background-color: #ff7675;
        color: white;
        padding: 0.5em 1.2em;
        text-decoration: none;
        border-radius: 10px;
        font-family: 'Noto Sans TC', sans-serif;
        font-weight: bold;
      ">⬅️ 返回首頁</a>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # 顯示 GPX 載入狀態
    html = m.get_root().render()
    html += "<div style='padding:1em;font-family:sans-serif'>"
    if loaded:
        html += "<h3>✅ 載入成功的 GPX：</h3><ul>"
        for f in loaded:
            html += f"<li>{f}</li>"
        html += "</ul>"
    if skipped:
        html += "<h3>⚠️ 未包含高雄區域的 GPX（已略過）：</h3><ul>"
        for f in skipped:
            html += f"<li>{f}</li>"
        html += "</ul>"
    if failed:
        html += "<h3>❌ 載入失敗的 GPX：</h3><ul>"
        for f, err in failed:
            html += f"<li>{f}<br><code>{err}</code></li>"
        html += "</ul>"
    html += "</div>"
    return html

def update_home_index(months):
    html = "<h1>🌍🐒 WorldGym 地圖首頁</h1><ul>"
    for m in sorted(months):
        html += f'<li><a href="{m}/index.html">{m}</a></li>'
    html += "</ul>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    folders = [f for f in os.listdir() if os.path.isdir(f) and f.startswith("2025-")]
    generated = []
    for folder in folders:
        print(f"📂 處理資料夾：{folder}")
        gpx_files = [f for f in os.listdir(folder) if f.endswith(".gpx")]
        print(f"🔍 發現 GPX 檔案：{gpx_files}")
        if not gpx_files:
            print(f"⚠️ {folder} 中沒有找到 GPX")
            continue
        html = generate_leaflet_html(gpx_files, folder)
        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        generated.append(folder)

    update_home_index(generated)
    print("✅ 所有 index.html 重新產生完成")

if __name__ == "__main__":
    main()

generate_homepage()
