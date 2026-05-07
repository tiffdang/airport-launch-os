import os
import folium
import osmnx as ox

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

AIRPORT_NAME = "San Francisco International Airport, California, USA"
CENTER = [37.6213, -122.3790]

# Download airport road network
G = ox.graph_from_place(
    AIRPORT_NAME,
    network_type="drive",
    simplify=True
)

nodes, edges = ox.graph_to_gdfs(G)

# Create base map
m = folium.Map(
    location=CENTER,
    zoom_start=14,
    tiles="CartoDB positron"
)

# Add road network
folium.GeoJson(
    edges,
    name="SFO Road Network",
    style_function=lambda feature: {
        "weight": 2,
        "opacity": 0.7,
    },
).add_to(m)

# Candidate pickup zones
pickup_zones = [
    {
        "name": "Terminal 2",
        "lat": 37.6175,
        "lon": -122.3867,
        "score": 84,
        "notes": "Balanced accessibility and congestion."
    },
    {
        "name": "Terminal 3",
        "lat": 37.6192,
        "lon": -122.3848,
        "score": 78,
        "notes": "High passenger demand."
    },
    {
        "name": "International Terminal",
        "lat": 37.6156,
        "lon": -122.3925,
        "score": 68,
        "notes": "Complex international arrivals flow."
    },
    {
        "name": "Garage G",
        "lat": 37.6206,
        "lon": -122.3907,
        "score": 91,
        "notes": "Potential controlled AV pickup zone."
    },
]

# Add pickup markers
for zone in pickup_zones:

    folium.CircleMarker(
        location=[zone["lat"], zone["lon"]],
        radius=10,
        fill=True,
        fill_opacity=0.85,
        popup=folium.Popup(
            f"""
            <b>{zone['name']}</b><br>
            Score: {zone['score']}/100<br>
            {zone['notes']}
            """,
            max_width=300,
        ),
        tooltip=f"{zone['name']} ({zone['score']}/100)",
    ).add_to(m)

# Recommended zone
recommended = max(pickup_zones, key=lambda z: z["score"])

folium.Marker(
    location=[recommended["lat"], recommended["lon"]],
    tooltip="Recommended Launch Zone",
    popup=f"Recommended Zone: {recommended['name']}",
    icon=folium.Icon(icon="star"),
).add_to(m)

# Save map
output_path = os.path.join(
    OUTPUT_DIR,
    "sfo_day1_airport_map.html"
)

m.save(output_path)

print(f"Map saved to: {output_path}")
print(f"Recommended launch zone: {recommended['name']}")