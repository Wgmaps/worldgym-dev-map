import os
import re
import json
import folium
import gpxpy
from folium.plugins import BeautifyIcon

# --- 核心改進：更聰明的「姓名抽取」 ---
def extract_name_from_filename(filename: str) -> str:
    """
    從檔名中抽出「業務姓名」做圖層歸類。
    規則：
    - 取第一段「非數字、非底線、非減號、非空白」的連續字串
      例：Amber1           -> Amber
          Amber_下午        -> Amber
          Amber-早上        -> Amber
          2025-10-31_Amber1 -> Amber
          亮亮2             -> 亮亮
    - 去掉姓名尾端的數字（如 Amber1 -> Amber）
    - 對於全大寫/小寫/混合大小寫會一起歸類（以第一次遇到的寫法當圖層標籤）
    """
    base = os.path.splitext(os.path.basename(filename))[0]
    m = re.search(r'[^\d_\-\s]+', base)
    if not m:
        return "Unknown"
    name = m.group(0)
    name = re.sub(r'\d+$', '', name)  # 去掉尾端連續數字
    return name if name else "Unknown"

def create_map(center, zoom_start=15):
    m = folium.Map(location=center, zoom_start=zoom_start, control_scale=True)

    # Base tiles
    folium.TileLayer("openstreetmap", name="開發路線").add_to(m)
    folium.TileLayer("cartodb positron", name="特約商家").add_to(m)
    return m

def add_gpx_routes(folder_path, map_object):
    # 使用「小寫」當 key 做去重；用第一次遇到的寫法當顯示名稱
    layer_dict = {}          # key: lower_name -> FeatureGroup
    display_name_dict = {}   # key: lower_name -> original display name (第一次遇到)

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".gpx"):
            continue

        person_name = extract_name_from_filename(filename)
        lower_key = person_name.lower()

        # 建立/取得圖層
        if lower_key not in layer_dict:
            display_name_dict[lower_key] = person_name  # 記住第一次遇到的寫法
            layer = folium.FeatureGroup(name=display_name_dict[lower_key])
            layer_dict[lower_key] = layer
            map_object.add_child(layer)

        # 繪線
        gpx_path = os.path.join(folder_path, filename)
        try:
            with open(gpx_path, "r", encoding="utf-8") as gpx_file:
                gpx = gpxpy.parse(gpx_file)
        except Exception:
            # 有些 GPX 可能不是 UTF-8，也嘗試無編碼宣告開啟
            with open(gpx_path, "r") as gpx_file:
                gpx = gpxpy.parse(gpx_file)

        for track in gpx.tracks:
            for segment in track.segments:
                points = [[pt.latitude, pt.longitude] for pt in segment.points]
                if points:
                    folium.PolyLine(
                        points,
                        color="blue",
                        weight=3,
                        opacity=0.8,
                        tooltip=filename
                    ).add_to(layer_dict[lower_key])

def add_shop_markers(shop_json_path, map_object):
    try:
        if not os.path.exists(shop_json_path):
            return
        with open(shop_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        features = data.get("features", [])
        group = folium.FeatureGroup(name="特約商家")
        for shop in features:
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
        # 不中斷產出，只是略過商家圖層
        print(f"[shops.json 載入失敗] {e}")

def add_home_marker(map_object, location):
    folium.Marker(
        location=location,
        popup="WorldGym 興楠店",
        icon=BeautifyIcon(
            icon="home",
            icon_shape="marker",
            border_color="green",
            text_color="white",
            background_color="green"
        )
    ).add_to(map_object)

def add_title(map_object, month, title="🦍🌍 WorldGym NZXN 每日開發地圖"):
    html = f"""<div style='position: fixed; top: 10px; left: 10px; z-index: 9999; 
                    background: white; padding: 10px 15px; border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3); font-size: 14px;'>
                <b>{title}</b><br>
                📅 月份：{month}<br>
                🔙 <a href='../index.html' style='color: blue;'>返回首頁</a>
              </div>"""
    map_object.get_root().html.add_child(folium.Element(html))

def generate(folder_name):
    # 固定新中心點（可依門市調整）
    map_center = [22.73008, 120.331844]
    m = create_map(map_center)
    add_gpx_routes(folder_name, m)
    add_shop_markers(os.path.join(folder_name, "shops.json"), m)
    add_home_marker(m, [22.73008, 120.331844])
    # 顯示月份（假設資料夾類似 2025-10）
    add_title(m, folder_name.split("-")[-1])
    folium.LayerControl().add_to(m)
    m.save(os.path.join(folder_name, "index.html"))

if __name__ == "__main__":
    current_folder = os.getcwd()
    for folder in os.listdir(current_folder):
        if folder.startswith("2025-"):
            generate(folder)
