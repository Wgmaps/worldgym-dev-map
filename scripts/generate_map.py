import os
import json
import folium
from folium.plugins import Fullscreen
import gpxpy
from datetime import datetime
from pathlib import Path

def load_shops(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 無法讀取 {json_path}: {e}")
        return []

def parse_gpx(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as gpx_file:
            return gpxpy.parse(gpx_file)
    except Exception as e:
        print(f"⚠️ GPX 解析錯誤 {file_path}: {e}")
        return None

def create_monthly_map(folder):
    month_map = folium.Map(location=[22.626, 120.315], zoom_start=13, tiles='OpenStreetMap')
    Fullscreen(position='topright').add_to(month_map)

    shop_path = folder / "shops.json"
    shops = load_shops(shop_path)

    shop_group = folium.FeatureGroup(name="🏪 商家地標", show=True)
    for shop in shops:
        try:
            lat = float(shop["lat"])
            lng = float(shop["lng"])
            name = shop["店家名稱"]
            address = shop["地址"]
            staff = shop.get("負責", "未知")
            popup = f"<b>{name}</b><br>{address}<br>負責人：{staff}"
            folium.Marker(location=[lat, lng], popup=popup, icon=folium.Icon(color="green")).add_to(shop_group)
        except Exception as e:
            print(f"⚠️ 無法新增商家地標: {shop} - {e}")
    shop_group.add_to(month_map)

    gpx_group = folium.FeatureGroup(name="📍 全部開發路線", show=True)
    for file in sorted(folder.glob("*.gpx")):
        gpx = parse_gpx(file)
        if not gpx:
            continue
        coords = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    coords.append((point.latitude, point.longitude))
        if coords:
            folium.PolyLine(locations=coords, weight=5, color='blue', opacity=0.6, tooltip=file.name).add_to(gpx_group)
    gpx_group.add_to(month_map)

    folium.LayerControl(collapsed=False).add_to(month_map)

    output_path = folder / "index.html"
    month_map.save(output_path)
    print(f"✅ 地圖已輸出到 {output_path}")

def generate_all_maps():
    root = Path(".")
    for folder in sorted(root.iterdir()):
        if folder.is_dir() and folder.name.startswith("2025-"):
            create_monthly_map(folder)

if __name__ == "__main__":
    generate_all_maps()
