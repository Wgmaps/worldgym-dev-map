
import folium
import os
import json
import gpxpy
from pathlib import Path

def generate_map(folder):
    # 正確中心點與公司位置
    center_lat, center_lon = 22.73008, 120.331844
    map_center = [center_lat, center_lon]

    m = folium.Map(location=map_center, zoom_start=15)

    # 圖層群組
    route_group = folium.FeatureGroup(name="🚴‍♀️ 開發路線")
    shop_group = folium.FeatureGroup(name="🛍️ 特約商家")

    # GPX 讀取
    gpx_files = [f for f in os.listdir(folder) if f.endswith(".gpx")]
    if gpx_files:
        for gpx_file in gpx_files:
            gpx_path = os.path.join(folder, gpx_file)
            with open(gpx_path, 'r', encoding='utf-8') as f:
                gpx = gpxpy.parse(f)

            for track in gpx.tracks:
                for segment in track.segments:
                    points = [(point.latitude, point.longitude) for point in segment.points]
                    folium.PolyLine(points, color="blue", weight=4.5, opacity=0.7).add_to(route_group)
        print(f"✅ 已加入 GPX 路線：{', '.join(gpx_files)}")
    else:
        print("⚠️ 無 GPX 路線")

    # 商家資料
    shops_path = os.path.join(folder, "shops.json")
    if os.path.exists(shops_path):
        with open(shops_path, 'r', encoding='utf-8') as f:
            shops_data = json.load(f).get("features", [])
        for shop in shops_data:
            geometry = shop.get("geometry", {})
            properties = shop.get("properties", {})
            coords = geometry.get("coordinates", [])
            if len(coords) == 2:
                lon, lat = coords
                name = properties.get("name", "商家")
                note = properties.get("note", "")
                emoji = properties.get("emoji", "")
                popup_html = f"""<div style='font-weight:bold; font-size:14px; min-width:120px;'>{emoji} {name}</div>
                <div style='font-size:12px; color:gray;'>{note}</div>"""
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_html,
                    icon=folium.Icon(color='red', icon='shopping-cart', prefix='fa')
                ).add_to(shop_group)
        print(f"✅ 已載入商家共 {len(shops_data)} 筆")
    else:
        print("⚠️ 沒有找到 shops.json")

    # 公司位置
    folium.Marker(
        location=[center_lat, center_lon],
        popup="🏠 公司位置",
        icon=folium.Icon(color='green', icon='home')
    ).add_to(m)

    # 加入圖層群組
    route_group.add_to(m)
    shop_group.add_to(m)
    folium.LayerControl().add_to(m)

    # 存檔
    m.save(os.path.join(folder, "index.html"))
    print(f"✅ 地圖已產出：{folder}/index.html")

# 範例執行（實際自動化由 GitHub Action 指定路徑）
if __name__ == "__main__":
    import sys
    folder_path = sys.argv[1] if len(sys.argv) > 1 else "2025-08"
    generate_map(folder_path)
