
import folium
import os
import gpxpy
from pathlib import Path

def parse_gpx_file(gpx_path):
    with open(gpx_path, 'r', encoding='utf-8') as f:
        gpx = gpxpy.parse(f)
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append((point.latitude, point.longitude))
    return points

def create_map(folder_path, output_path):
    center_lat, center_lon = 22.73008, 120.331844
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=15, control_scale=True)

    feature_groups = {}
    folder = Path(folder_path)
    for gpx_file in folder.glob("*.gpx"):
        name = gpx_file.stem
        user = name.split("_")[1] if "_" in name else "未分類"
        points = parse_gpx_file(gpx_file)
        if not points:
            continue
        fg = feature_groups.setdefault(user, folium.FeatureGroup(name=user, show=True))
        folium.PolyLine(points, color="blue", weight=4, opacity=0.8, tooltip=name).add_to(fg)

    for fg in feature_groups.values():
        fg.add_to(fmap)

    # 加公司地點
    folium.Marker(
        location=[22.73008, 120.331844],
        popup="🏢 公司位置",
        icon=folium.Icon(color="green", icon="building", prefix="fa")
    ).add_to(fmap)

    folium.LayerControl(collapsed=False).add_to(fmap)

    # 自訂 HTML
    title_html = '''
        <div style="position: fixed; top: 10px; left: 10px; z-index: 9999; background-color: white; padding: 10px;
                    border: 2px solid black; border-radius: 5px; font-size: 16px;">
            <b>🦍🌍 WorldGym 分店 每日開發地圖</b><br>
            🗓️ 月份：{month}<br>
            <a href="../index.html" style="color: blue;">🔙 返回首頁</a>
        </div>
    '''.format(month=os.path.basename(folder_path))
    fmap.get_root().html.add_child(folium.Element(title_html))

    fmap.save(output_path)

if __name__ == "__main__":
    for folder in Path(".").glob("2025-*"):
        if folder.is_dir():
            output_file = folder / "index.html"
            create_map(folder, output_file)
