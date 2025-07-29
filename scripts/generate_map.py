
import os
import folium
import gpxpy
from folium.plugins import BeautifyIcon
import json

def extract_name_from_filename(filename):
    return filename.split("_")[1].split(".")[0] if "_" in filename else "Unknown"

def create_map(center, zoom_start=15):
    m = folium.Map(location=center, zoom_start=zoom_start, control_scale=True)

    # Base tiles
    folium.TileLayer("openstreetmap", name="開發路線").add_to(m)
    folium.TileLayer("cartodb positron", name="特約商家").add_to(m)

    return m

def add_gpx_routes(folder_path, map_object):
    layer_dict = {}

    for filename in os.listdir(folder_path):
        if filename.endswith(".gpx"):
            person_name = extract_name_from_filename(filename)
            if person_name not in layer_dict:
                layer_dict[person_name] = folium.FeatureGroup(name=person_name)
                map_object.add_child(layer_dict[person_name])

            with open(os.path.join(folder_path, filename), "r") as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                for track in gpx.tracks:
                    for segment in track.segments:
                        points = [[point.latitude, point.longitude] for point in segment.points]
                        if points:
                            folium.PolyLine(points, color="blue", weight=3, opacity=0.8,
                                            tooltip=filename).add_to(layer_dict[person_name])

def add_shop_markers(shop_json_path, map_object):
    try:
        with open(shop_json_path, "r", encoding="utf-8") as f:
            shops_json = json.load(f)
            shops_data = shops_json.get("features", [])
            group = folium.FeatureGroup(name="特約商家")
            for shop in shops_data:
                geometry = shop.get("geometry", {})
                properties = shop.get("properties", {})
                coords = geometry.get("coordinates", [])
                if len(coords) == 2:
                    lon, lat = coords
                    name = properties.get("name", "商家")
                    note = properties.get("note", "")
                    emoji = properties.get("emoji", "")
                    popup_html = f"<b>{emoji} {name}</b><br><span style='color:gray'>{note}</span>"
                    group.add_child(folium.Marker(
                        location=[lat, lon],
                        popup=popup_html,
                        icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
                    ))
            map_object.add_child(group)
    except Exception as e:
        print(f"商家資料載入失敗: {e}")

def add_home_marker(map_object, location, popup_text="公司位置"):
    folium.Marker(
        location=location,
        popup=popup_text,
        icon=BeautifyIcon(
            icon="fa-building",
            border_color="black",
            text_color="white",
            background_color="green"
        )
    ).add_to(map_object)

def add_title(map_object, month, title="🦍🌍 WorldGym HZ 每日開發地圖"):
    html = f"""<div style='position: fixed; top: 10px; left: 10px; z-index: 9999; 
                    background: white; padding: 10px 15px; border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3); font-size: 14px;'>
                <b>{title}</b><br>
                📅 月份：{month}<br>
                🔙 <a href='../index.html' style='color: blue;'>返回首頁</a>
              </div>"""
    map_object.get_root().html.add_child(folium.Element(html))

def generate(folder_name):
    map_center = [22.73008, 120.331844]  # 新中心點
    m = create_map(map_center)
    add_gpx_routes(folder_name, m)
    add_shop_markers(os.path.join(folder_name, "shops.json"), m)
    add_home_marker(m, [22.73008, 120.331844])
    add_title(m, folder_name.split("-")[-1])
    folium.LayerControl().add_to(m)
    m.save(os.path.join(folder_name, "index.html"))

if __name__ == "__main__":
    current_folder = os.getcwd()
    for folder in os.listdir(current_folder):
        if folder.startswith("2025-"):
            generate(folder)
