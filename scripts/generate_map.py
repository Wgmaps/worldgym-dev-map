
import os
import json
import folium
from folium import FeatureGroup, LayerControl
from folium.plugins import Search
import gpxpy

def generate_map_for_folder(gpx_folder):
    m = folium.Map(location=[22.626, 120.315], zoom_start=15)

    merchant_layer = folium.FeatureGroup(name="🛍️ 特約商家")
    m.add_child(merchant_layer)

    shops_file = os.path.join(gpx_folder, 'shops.json')
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
                        popup_html = f"<b>{emoji} {name}</b><br>{note}"
                        folium.Marker(
                            location=[lat, lon],
                            popup=popup_html,
                            icon=folium.Icon(color="red", icon="shopping-cart", prefix='fa')
                        ).add_to(merchant_layer)
        except Exception as e:
            print(f"❌ 無法讀取商家資料檔: {e}")

    gpx_files = [f for f in os.listdir(gpx_folder) if f.endswith('.gpx')]
    agent_layers = {}

    for gpx_file in gpx_files:
        filepath = os.path.join(gpx_folder, gpx_file)
        with open(filepath, 'r', encoding='utf-8') as f:
            gpx = gpxpy.parse(f)

        if gpx.tracks:
            track = gpx.tracks[0]
            name = track.name or os.path.splitext(gpx_file)[0]
            coords = [(p.latitude, p.longitude) for s in track.segments for p in s.points]
            if not coords:
                continue

            agent_name = name.split()[0]
            if agent_name not in agent_layers:
                agent_layers[agent_name] = folium.FeatureGroup(name=agent_name)
                m.add_child(agent_layers[agent_name])

            folium.PolyLine(
                locations=coords,
                color="blue",
                weight=3,
                opacity=0.8,
                tooltip=name
            ).add_to(agent_layers[agent_name])

    LayerControl(collapsed=False).add_to(m)

    output_file = os.path.join(gpx_folder, "index.html")
    m.save(output_file)
    print(f"✅ 地圖已儲存至: {output_file}")
