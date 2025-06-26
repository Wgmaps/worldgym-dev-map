import re

root = Path(".")
month_folders = sorted([f for f in root.iterdir() if f.is_dir() and re.match(r"^\d{4}-\d{2}$", f.name)])

for folder in month_folders:
    print(f"📍 正在處理資料夾：{folder}")
    gpx_files = list(folder.glob("*.gpx"))
    shops_file = folder / "shops.json"
    output_html = folder / "index.html"

    if not gpx_files:
        print(f"⚠️ 沒有找到 GPX 檔案，跳過 {folder}")
        continue

    # Map init
    from folium import Map, LayerControl, FeatureGroup, Marker, GeoJson
    import json
    import gpxpy
    import folium

    m = Map(location=[22.626, 120.301], zoom_start=13, control_scale=True)

    # 加入 GPX 路線
    gpx_group = FeatureGroup(name="📍員工開發路線", show=True)
    for gpx_file in gpx_files:
        with open(gpx_file, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)
            for track in gpx.tracks:
                for segment in track.segments:
                    coords = [(point.latitude, point.longitude) for point in segment.points]
                    if coords:
                        folium.PolyLine(coords, color="blue", weight=3).add_to(gpx_group)
    gpx_group.add_to(m)

    # 加入商家地標
    if shops_file.exists():
        shop_group = FeatureGroup(name="🏪 商家地標", show=True)
        with open(shops_file, "r", encoding="utf-8") as f:
            shops = json.load(f)
            for shop in shops:
                location = [shop["lat"], shop["lng"]]
                text = shop.get("name", "")
                Marker(location=location, tooltip=f"📍 {text}").add_to(shop_group)
        shop_group.add_to(m)

    LayerControl(collapsed=False).add_to(m)
    m.save(str(output_html))
    print(f"✅ 地圖已輸出：{output_html}")
exit(0)