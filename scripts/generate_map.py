import os
import json
import folium
import gpxpy

# 資料夾設定
folder = os.path.basename(os.getcwd())
gpx_files = [f for f in os.listdir() if f.endswith(".gpx")]
shop_file = "shops.json"

# 初始化地圖
m = folium.Map(location=[22.9986, 120.2269], zoom_start=13, control_scale=True)

# 員工路線圖層
track_layer = folium.FeatureGroup(name="👟 員工開發路線")
for gpx_file in gpx_files:
    try:
        with open(gpx_file, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)
            for track in gpx.tracks:
                for segment in track.segments:
                    coords = [(p.latitude, p.longitude) for p in segment.points]
                    if coords:
                        folium.PolyLine(coords, color="blue", weight=3, tooltip=gpx_file).add_to(track_layer)
    except Exception as e:
        print(f"⚠️ GPX讀取失敗: {gpx_file} -> {e}")

track_layer.add_to(m)

# 商家圖層
if os.path.exists(shop_file):
    try:
        with open(shop_file, "r", encoding="utf-8") as f:
            shops = json.load(f)
            shop_layer = folium.FeatureGroup(name="📍 商家地標")
            for shop in shops:
                lat = shop.get("lat")
                lon = shop.get("lon")
                name = shop.get("name")
                note = shop.get("note", "")
                if lat and lon:
                    folium.Marker(
                        location=[lat, lon],
                        tooltip=f"📍{name}",
                        popup=folium.Popup(note, max_width=300)
                    ).add_to(shop_layer)
            shop_layer.add_to(m)
    except Exception as e:
        print(f"⚠️ 商家載入失敗: {e}")

# 控制項
folium.LayerControl().add_to(m)

# 標題與返回按鈕
title_html = f"""
<h2 style='text-align:center;font-family: Noto Sans TC;'>🐷🌏 WorldGym NZXN 每日開發地圖 {folder} 💰</h2>
<div style='text-align:center;margin-bottom:1em;'>
  <a href='../index.html' style='background-color:#f76775;color:white;padding:0.5em 1.2em;text-decoration:none;border-radius:10px;
  font-family:Noto Sans TC;font-weight:bold;'>⏪ 返回首頁</a>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

# 儲存地圖
m.save("index.html")
print("✅ 地圖生成完成：index.html")
