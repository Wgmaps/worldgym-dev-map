
import os
import folium
import gpxpy
import gpxpy.gpx
import json

# 定義高雄的範圍 (粗略矩形)：經度與緯度範圍
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
    center = [22.63, 120.30]  # 高雄市中心
    m = folium.Map(location=center, zoom_start=13)
    loaded = []
    skipped = []
    failed = []

    for gpx_file in gpx_files:
        try:
            with open(os.path.join(folder, gpx_file), 'r', encoding='utf-8') as f:
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

    # 加入載入狀態說明
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
            html += f"<li>{f} - {err}</li>"
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
