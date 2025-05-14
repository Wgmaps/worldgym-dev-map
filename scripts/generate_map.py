
import os
import folium
import gpxpy
import gpxpy.gpx
import json

def generate_leaflet_html(gpx_files, folder):
    center = [25.0330, 121.5654]
    m = folium.Map(location=center, zoom_start=11)
    loaded = []
    failed = []

    for gpx_file in gpx_files:
        try:
            with open(os.path.join(folder, gpx_file), 'r', encoding='utf-8') as f:
                gpx = gpxpy.parse(f)

            track = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": []
                },
                "properties": {"name": gpx_file}
            }

            for track_seg in gpx.tracks[0].segments:
                for point in track_seg.points:
                    track["geometry"]["coordinates"].append([point.longitude, point.latitude])

            folium.GeoJson(track, name=gpx_file, tooltip=gpx_file).add_to(m)
            loaded.append(gpx_file)
        except Exception as e:
            failed.append((gpx_file, str(e)))

    # 在頁面上標示載入成功與失敗的清單
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
            html += f"<li>{f} - {err}</li>"
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
