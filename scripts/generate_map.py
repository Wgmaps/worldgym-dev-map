import os
import folium
import gpxpy
import gpxpy.gpx
from datetime import datetime

def generate_leaflet_html(gpx_files, folder):
    m = folium.Map(location=[25.0330, 121.5654], zoom_start=11)
    loaded = []
    failed = []

    for gpx_file in gpx_files:
        try:
            with open(os.path.join(folder, gpx_file), 'r', encoding='utf-8') as f:
                gpx = gpxpy.parse(f)

            for track in gpx.tracks:
                for segment in track.segments:
                    points = [(p.latitude, p.longitude) for p in segment.points]
                    if not points:
                        raise ValueError("GPX 檔案中沒有座標點")
                    name = gpx_file
                    date_str = ""
                    if segment.points and segment.points[0].time:
                        date_str = segment.points[0].time.strftime("%Y-%m-%d")
                        name += f" ({date_str})"

                    folium.PolyLine(points, color='red', weight=3, tooltip=name).add_to(m)
                    loaded.append(name)
        except Exception as e:
            failed.append((gpx_file, str(e)))

    # 插入標題與回首頁按鈕
    header_html = '''
    <h2 style="text-align: center; font-family: sans-serif;">
        WorldGym 每日開發路線圖 - {folder}
    </h2>
    <div style="text-align: center; margin-bottom: 10px;">
        <a href="../index.html" style="
            background: #555;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 6px;
            font-family: sans-serif;
        ">⬅️ 返回首頁</a>
    </div>
    '''.replace("{folder}", folder)
    m.get_root().html.add_child(folium.Element(header_html))

    html = m.get_root().render()
    html += "<div style='padding:1em;font-family:sans-serif'>"
    if loaded:
        html += "<h3>✅ 載入成功的 GPX：</h3><ul>"
        for f in loaded:
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
    html = "<h1>WorldGym 地圖首頁</h1><ul>"
    for m in sorted(months):
        html += f'<li><a href="{m}/index.html">{m}</a></li>'
    html += "</ul>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    folders = [f for f in os.listdir() if os.path.isdir(f) and f.startswith("2025-")]
    generated = []
    for folder in folders:
        gpx_files = [f for f in os.listdir(folder) if f.endswith(".gpx")]
        if not gpx_files:
            continue
        html = generate_leaflet_html(gpx_files, folder)
        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        generated.append(folder)

    update_home_index(generated)
    print("✅ 所有 index.html 重新產生完成")

if __name__ == "__main__":
    main()
