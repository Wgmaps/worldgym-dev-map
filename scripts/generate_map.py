import os
import re
import sys
import json
import folium
import gpxpy
from folium.plugins import BeautifyIcon


# --- 核心改進：更聰明的「姓名抽取」 ---
def extract_name_from_filename(filename: str) -> str:
    """從檔名中抽出業務姓名，作為地圖圖層名稱。"""
    base = os.path.splitext(os.path.basename(filename))[0]
    match = re.search(r"[^\d_\-\s]+", base)
    if not match:
        return "Unknown"

    name = re.sub(r"\d+$", "", match.group(0))
    return name if name else "Unknown"


def create_map(center, zoom_start=15):
    map_object = folium.Map(
        location=center,
        zoom_start=zoom_start,
        control_scale=True,
    )
    folium.TileLayer("openstreetmap", name="開發路線").add_to(map_object)
    folium.TileLayer("cartodb positron", name="特約商家").add_to(map_object)
    return map_object


def add_gpx_routes(folder_path, map_object):
    """
    逐一讀取 GPX。

    單一檔案損壞、編碼錯誤或不是有效 GPX 時，只跳過該檔案，
    不讓整個月份及後續月份的地圖產生作業失敗。
    """
    layer_dict = {}
    display_name_dict = {}
    success_count = 0
    skipped_count = 0

    for filename in sorted(os.listdir(folder_path)):
        if not filename.lower().endswith(".gpx"):
            continue

        gpx_path = os.path.join(folder_path, filename)

        try:
            # 使用二進位模式，交由 XML/GPX 解析器處理檔案宣告的編碼。
            with open(gpx_path, "rb") as gpx_file:
                gpx = gpxpy.parse(gpx_file)
        except Exception as error:
            skipped_count += 1
            print(
                f"⚠️ 跳過無法讀取的 GPX：{gpx_path}\n"
                f"   錯誤類型：{type(error).__name__}\n"
                f"   錯誤內容：{error}"
            )
            continue

        person_name = extract_name_from_filename(filename)
        lower_key = person_name.lower()

        if lower_key not in layer_dict:
            display_name_dict[lower_key] = person_name
            layer = folium.FeatureGroup(name=display_name_dict[lower_key])
            layer_dict[lower_key] = layer
            map_object.add_child(layer)

        has_points = False
        for track in gpx.tracks:
            for segment in track.segments:
                points = [
                    [point.latitude, point.longitude]
                    for point in segment.points
                    if point.latitude is not None and point.longitude is not None
                ]
                if points:
                    has_points = True
                    folium.PolyLine(
                        points,
                        color="blue",
                        weight=3,
                        opacity=0.8,
                        tooltip=filename,
                    ).add_to(layer_dict[lower_key])

        if has_points:
            success_count += 1
        else:
            print(f"ℹ️ GPX 沒有可顯示的軌跡點：{gpx_path}")

    print(
        f"✅ {folder_path} GPX 處理完成：成功 {success_count} 個，跳過 {skipped_count} 個"
    )


def add_shop_markers(shop_json_path, map_object):
    try:
        if not os.path.exists(shop_json_path):
            return

        with open(shop_json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

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
                popup_html = (
                    f"<b>{emoji} {name}</b><br>"
                    f"<span style='color:gray'>{note}</span>"
                )
                group.add_child(
                    folium.Marker(
                        location=[lat, lon],
                        popup=popup_html,
                        icon=folium.Icon(
                            color="red",
                            icon="shopping-cart",
                            prefix="fa",
                        ),
                    )
                )

        map_object.add_child(group)
    except Exception as error:
        print(f"⚠️ shops.json 載入失敗，略過商家資料：{shop_json_path}")
        print(f"   錯誤類型：{type(error).__name__}")
        print(f"   錯誤內容：{error}")


def add_home_marker(map_object, location):
    folium.Marker(
        location=location,
        popup="WorldGym 興楠店",
        icon=BeautifyIcon(
            icon="home",
            icon_shape="marker",
            border_color="green",
            text_color="white",
            background_color="green",
        ),
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
    if not os.path.isdir(folder_name):
        print(f"⚠️ 找不到月份資料夾，跳過：{folder_name}")
        return

    print(f"🔄 開始產生地圖：{folder_name}")
    map_center = [22.73008, 120.331844]
    map_object = create_map(map_center)

    add_gpx_routes(folder_name, map_object)
    add_shop_markers(os.path.join(folder_name, "shops.json"), map_object)
    add_home_marker(map_object, map_center)
    add_title(map_object, folder_name.split("-")[-1])
    folium.LayerControl().add_to(map_object)

    output_path = os.path.join(folder_name, "index.html")
    map_object.save(output_path)
    print(f"✅ 地圖已產生：{output_path}")


if __name__ == "__main__":
    month_pattern = re.compile(r"^\d{4}-\d{2}$")

    # build.yml 會傳入單一月份，例如：python scripts/generate_map.py 2026-07
    if len(sys.argv) > 1:
        requested_folder = sys.argv[1].rstrip("/\\")
        if not month_pattern.match(os.path.basename(requested_folder)):
            print(f"❌ 月份資料夾名稱格式錯誤：{requested_folder}")
            sys.exit(1)
        generate(requested_folder)
    else:
        # 手動執行且未指定月份時，才產生所有月份。
        current_folder = os.getcwd()
        for folder in sorted(os.listdir(current_folder)):
            if month_pattern.match(folder) and os.path.isdir(folder):
                generate(folder)
