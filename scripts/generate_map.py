
import os
import glob
import folium
from folium.plugins import BeautifyIcon
import gpxpy
from datetime import datetime

def generate_map_for_folder(folder):
    m = folium.Map(location=[22.729, 120.327], zoom_start=13)
    gpx_status_html = "<h3>✅ 載入成功的 GPX：</h3><ul>"
    feature_groups = {}

    shops_file = os.path.join(folder, "shops.txt")
    if os.path.exists(shops_file):
        with open(shops_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    lat, lon, name = parts[0], parts[1], ",".join(parts[2:])
                    folium.Marker(
                        location=[float(lat), float(lon)],
                        popup=name,
                        icon=BeautifyIcon(
                            icon="store",
                            border_color="#FF0000",
                            text_color="#FF0000",
                            background_color="#FFF0F0",
                            number=chr(9733)
                        )
                    ).add_to(m)

    gpx_files = sorted(glob.glob(os.path.join(folder, "*.gpx")))
    for gpx_file in gpx_files:
        try:
            with open(gpx_file, "r", encoding="utf-8") as f:
                gpx = gpxpy.parse(f)
                coords = [(point.latitude, point.longitude) for track in gpx.tracks for segment in track.segments for point in segment.points]
                if coords:
                    name = os.path.basename(gpx_file)
                    fg = folium.FeatureGroup(name=name)
                    folium.PolyLine(coords, color="blue", weight=3, opacity=0.7, tooltip=name).add_to(fg)
                    fg.add_to(m)
                    feature_groups[name] = fg
                    gpx_status_html += f"<li>{name}</li>"
        except Exception as e:
            print(f"❌ Failed to load {gpx_file}: {e}")

    gpx_status_html += "</ul>"

    folium.LayerControl().add_to(m)
    gpx_status_element = folium.Element(gpx_status_html)
    m.get_root().html.add_child(gpx_status_element)

    title_html = '''
        <h2 style="position:fixed;top:10px;left:10px;z-index:9999;
            background:white;padding:5px 10px;border-radius:5px;">
            🦍🌍 WorldGym NZXN 每日開發地圖 2025-06 💰
            <a href="../index.html" style="margin-left:20px;">
                <button style="background:red;color:white;">返回首頁</button>
            </a>
        </h2>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    map_file = os.path.join(folder, "index.html")
    m.save(map_file)

def generate_homepage():
    folders = sorted([f for f in os.listdir("docs") if os.path.isdir(os.path.join("docs", f))])
    homepage_html = "<h1>WorldGym NZXN 每日開發地圖</h1><ul>"
    for folder in folders:
        homepage_html += f'<li><a href="{folder}/index.html">{folder}</a></li>'
    homepage_html += "</ul>"

    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(homepage_html)

if __name__ == "__main__":
    for folder in sorted(os.listdir("docs")):
        full_path = os.path.join("docs", folder)
        if os.path.isdir(full_path):
            generate_map_for_folder(full_path)
    generate_homepage()
