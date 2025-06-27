
import os
import json
import folium
import gpxpy

# 自動處理所有月份資料夾
folders = sorted([f for f in os.listdir() if os.path.isdir(f) and f.startswith("2025-")])

def generate_map_for_folder(gpx_folder):
    print(f"📍 處理資料夾：{gpx_folder}")
    m = folium.Map(location=[22.7279, 120.3285], zoom_start=13, control_scale=True)

    gpx_files = [f for f in os.listdir(gpx_folder) if f.endswith('.gpx')]

    # 加上開頭 HTML 標題與返回首頁
    title_html = f'''
         <h3 align="center" style="font-size:24px">
         🦍🌍 WorldGym NZXN 每日開發地圖 {gpx_folder} 💰
         </h3>
         <div style="text-align:center;margin-bottom:10px;">
         <a href="../index.html"><button style="background-color:red;color:white;border:none;padding:5px 10px;border-radius:5px;">返回首頁</button></a>
         </div>
     '''
    m.get_root().html.add_child(folium.Element(title_html))

    loaded_routes = []
    skipped = []
    failed = []
    skipped = []

    for gpx_file in sorted(gpx_files):
        file_path = os.path.join(gpx_folder, gpx_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                gpx = gpxpy.parse(f)
            for track in gpx.tracks:
                for segment in track.segments:
                    coords = [(point.latitude, point.longitude) for point in segment.points]
                    if coords:
                        loaded_routes.append((coords, gpx_file))
        except Exception as e:
            print(f"❌ 無法讀取 {gpx_file}: {e}")

    if loaded_routes:
        track_group = folium.FeatureGroup(name="🚴‍♂️員工開發路線", show=True)
        for coords, name in loaded_routes:
            folium.PolyLine(coords, color="blue", weight=4.5, opacity=0.8, tooltip=name).add_to(track_group)
        track_group.add_to(m)

    try:
        with open(os.path.join(gpx_folder, "shops.json"), "r", encoding="utf-8") as f:
            shop_data = json.load(f)
        shop_group = folium.FeatureGroup(name="📍開發商家", show=True)
        for feature in shop_data["features"]:
            props = feature["properties"]
            lat, lon = feature["geometry"]["coordinates"][1], feature["geometry"]["coordinates"][0]
            name = props.get("name", "未命名")
            note = props.get("note", "")
            emoji = props.get("emoji", "📍")
            popup = folium.Popup(f"<b>{emoji} {name}</b><br>{note}", max_width=300)
            folium.Marker(location=[lat, lon], popup=popup, icon=folium.Icon(color="red", icon="info-sign")).add_to(shop_group)
        shop_group.add_to(m)
    except Exception as e:
        print(f"⚠️ 無法載入商家資料: {e}")

    folium.LayerControl(collapsed=False).add_to(m)

    # 顯示已成功載入的 GPX 檔案清單
    if loaded_routes:
        gpx_list_html = "<div style='padding:10px;font-size:14px'><b>✅ 已成功載入以下 GPX 檔案：</b><ul>"
        for _, name in loaded_routes:
            gpx_list_html += f"<li>・{name}</li>"
        gpx_list_html += "</ul></div>"
        m.get_root().html.add_child(folium.Element(gpx_list_html))

    # 顯示 GPX 載入狀態（成功、略過、失敗）
    gpx_status_html = "<div style='padding:1em;font-family:sans-serif'>"
    if loaded_routes:
        gpx_status_html += "<h3>✅ 載入成功的 GPX：</h3><ul>"
        for _, name in loaded_routes:
            gpx_status_html += f"<li>{name}</li>"
        gpx_status_html += "</ul>"
    if skipped:
        gpx_status_html += "<h3>⚠️ 未包含高雄區域的 GPX（已略過）：</h3><ul>"
        for name in skipped:
            gpx_status_html += f"<li>{name}</li>"
        gpx_status_html += "</ul>"
    if failed:
        gpx_status_html += "<h3>❌ 載入失敗的 GPX：</h3><ul>"
        for name, err in failed:
            gpx_status_html += f"<li>{name}<br><code>{err}</code></li>"
        gpx_status_html += "</ul>"
    gpx_status_html += "</div>"

    m.get_root().html.add_child(folium.Element(gpx_status_html))
    m.save(os.path.join(gpx_folder, "index.html"))
    print(f"✅ 已產出 {gpx_folder}/index.html")

# 為每個資料夾產生地圖
for folder in folders:
    generate_map_for_folder(folder)

# 建立首頁 index.html
def generate_homepage():
    html = "<h1>🌍 WorldGym 地圖首頁</h1><ul>"
    for folder in folders:
        html += f'<li><a href="{folder}/index.html">{folder}</a></li>'
    html += "</ul>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

generate_homepage()
