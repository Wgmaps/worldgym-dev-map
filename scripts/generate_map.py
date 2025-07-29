import os
import json
import folium
from folium import FeatureGroup, LayerControl
from folium.plugins import Search
import gpxpy

def generate_map_for_folder(gpx_folder):
    try:
        print(f"📁 資料夾來源：{gpx_folder}")
        gpx_files = [f for f in os.listdir(gpx_folder) if f.endswith('.gpx')]
        print(f"🔍 找到的 GPX 檔案：{gpx_files}")
        if not gpx_files:
            print("⚠️ 找不到 GPX 檔案，略過這個資料夾")
            return

        shops_file = os.path.join(gpx_folder, 'shops.json')
        if not os.path.exists(shops_file):
            print("⚠️ 找不到 shops.json，略過商家地標")

        m = folium.Map(location=[22.7298662, 120.2656636], zoom_start=15)

    # 公司位置標記
    folium.Marker(
        location=[22.7298662, 120.2656636],
        popup="🏢 公司位置",
        icon=folium.Icon(color='green', icon='home', prefix='fa')
    ).add_to(m)


        # 加入商家地標
        if os.path.exists(shops_file):
            try:
                with open(shops_file, 'r', encoding='utf-8') as f:
                    shops_json = json.load(f)
                    shops_data = shops_json.get("features", [])
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
                            ).add_to(m)
            except Exception as e:
                print(f"⚠️ 商家地標處理失敗：{e}")

        # 載入 GPX 路線
        for gpx_file in gpx_files:
            full_path = os.path.join(gpx_folder, gpx_file)
            with open(full_path, 'r', encoding='utf-8') as gpx_f:
                gpx = gpxpy.parse(gpx_f)
                for track in gpx.tracks:
                    for segment in track.segments:
                        points = [(point.latitude, point.longitude) for point in segment.points]
                        folium.PolyLine(points, color="blue", weight=3).add_to(m)

        # 顯示商家圖層開關
        LayerControl().add_to(m)

        # 自動加入標題與返回首頁區塊
        folder_parts = os.path.normpath(gpx_folder).split(os.sep)
        store_code = folder_parts[-2] if len(folder_parts) >= 2 else "分店"
        month_code = folder_parts[-1] if len(folder_parts) >= 1 else "月份"

        header_html = f"""<div style='position: fixed; top: 10px; left: 10px; z-index: 9999; background: white;
                    padding: 10px 15px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                    font-family: sans-serif;'>
          <div style='font-size: 14px; font-weight: bold;'>
            <a href='../index.html' style='color: red; text-decoration: none;'>🔙 返回首頁</a>
          </div>
          <div style='margin-top: 5px; font-size: 18px;'>🦍🌍 <b>WorldGym {store_code} 每日開發地圖</b></div>
          <div style='font-size: 14px; margin-top: 5px;'>📅 月份：<b>{month_code}</b> 💰</div>
        </div>"""
        m.get_root().html.add_child(folium.Element(header_html))

        output_path = os.path.join(gpx_folder, "index.html")
        m.save(output_path)
        print(f"✅ 已成功產出地圖：{output_path}")
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

import sys
if __name__ == "__main__":
    generate_map_for_folder(sys.argv[1])
