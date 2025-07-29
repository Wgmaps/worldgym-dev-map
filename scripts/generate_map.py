
import os
import folium
import gpxpy
import json

gpx_folder = os.environ.get("GPX_FOLDER", ".")

# 中心座標
center = [22.73008, 120.331844]
m = folium.Map(location=center, zoom_start=15)

# 新增圖層控制器
layer_control = folium.map.LayerControl(collapsed=False)

# 商家地標
shops_path = os.path.join(gpx_folder, "shops.json")
if os.path.exists(shops_path):
    try:
        with open(shops_path, "r", encoding="utf-8") as f:
            shops_data = json.load(f).get("features", [])
            for shop in shops_data:
                geometry = shop.get("geometry", {})
                props = shop.get("properties", {})
                coords = geometry.get("coordinates", [])
                if len(coords) == 2:
                    lon, lat = coords
                    name = props.get("name", "商家")
                    note = props.get("note", "")
                    emoji = props.get("emoji", "")
                    popup_html = f"<div style='font-weight:bold;'>{emoji} {name}</div><div style='font-size:12px; color:gray;'>{note}</div>"
                    folium.Marker(
                        location=[lat, lon],
                        popup=popup_html,
                        icon=folium.Icon(color='red', icon='shopping-cart', prefix='fa')
                    ).add_to(m)
    except Exception as e:
        print(f"商家標記載入錯誤: {e}")

# 公司位置
folium.Marker(
    location=center,
    popup="🏠 公司位置",
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# 載入所有 .gpx 檔案，依人名建立圖層群組
for filename in os.listdir(gpx_folder):
    if filename.endswith(".gpx"):
        filepath = os.path.join(gpx_folder, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                name_key = filename.split("_")[1].replace(".gpx", "")
                if not name_key:
                    name_key = "路線"

                # 如果該人名圖層不存在就創建
                if name_key not in m._children:
                    group = folium.FeatureGroup(name=name_key)
                    m.add_child(group)
                else:
                    group = m._children[name_key]

                for track in gpx.tracks:
                    for segment in track.segments:
                        points = [(point.latitude, point.longitude) for point in segment.points]
                        folium.PolyLine(
                            points,
                            color="blue",
                            weight=4,
                            opacity=0.7,
                            tooltip=filename  # 滑鼠提示
                        ).add_to(group)

        except Exception as e:
            print(f"❌ 無法載入 {filename}: {e}")

# 加入圖層控制器與首頁按鈕
layer_control.add_to(m)
home_button = folium.Html('<a href="../index.html" style="position:absolute;top:10px;left:10px;z-index:9999;font-weight:bold;font-size:16px;background:white;padding:5px;border-radius:4px;text-decoration:none;">🏠 返回首頁</a>', script=True)
folium.Marker(center, icon=folium.DivIcon(html=home_button)).add_to(m)

# 儲存地圖
output_path = os.path.join(gpx_folder, "index.html")
m.save(output_path)
