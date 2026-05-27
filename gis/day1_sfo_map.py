import os
import folium
from folium.plugins import HeatMap
import osmnx as ox
from terminado.uimodule import Terminal
# Scenario mode options:
# "normal", "peak_hour", "late_night", "event_surge", "construction"
import sys
import pandas as pd

SCENARIO = sys.argv[1] if len(sys.argv) > 1 else "peak_hour"

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
def apply_scenario_adjustments(zone, scenario):
    adjusted_zone = zone.copy()

    if scenario == "peak_hour":
        adjusted_zone["score"] -= 8
        adjusted_zone["traffic_complexity"] -= 10
        adjusted_zone["pedestrian_conflict"] -= 8
        adjusted_zone["notes"] += " Peak hour increases curb pressure and pedestrian conflict."

    elif scenario == "late_night":
        adjusted_zone["score"] += 5
        adjusted_zone["traffic_complexity"] += 8
        adjusted_zone["pedestrian_conflict"] += 5
        adjusted_zone["notes"] += " Late night conditions reduce congestion and improve AV feasibility."

    elif scenario == "event_surge":
        adjusted_zone["score"] -= 12
        adjusted_zone["traffic_complexity"] -= 15
        adjusted_zone["pedestrian_conflict"] -= 12
        adjusted_zone["notes"] += " Event surge creates abnormal demand and passenger clustering."

    elif scenario == "construction":
        adjusted_zone["score"] -= 10
        adjusted_zone["curb_control"] -= 15
        adjusted_zone["staging_feasibility"] -= 10
        adjusted_zone["notes"] += " Construction reduces curb control and staging flexibility."

    adjusted_zone["score"] = max(0, min(100, adjusted_zone["score"]))

    return adjusted_zone
# Candidate pickup zones
pickup_zones = [
    {
        "name": "Terminal 2",
        "lat": 37.6175,
        "lon": -122.3867,
        "score": 77.8,
        "category": "Strong",
        "terminal_access": 85,
        "curb_control": 75,
        "traffic_complexity": 65,
        "pedestrian_conflict": 70,
        "staging_feasibility": 80,
        "rider_clarity": 85,
        "notes": "Balanced accessibility and congestion."
    },
    {
        "name": "Terminal 3",
        "lat": 37.6192,
        "lon": -122.3848,
        "score": 71.2,
        "category": "Moderate",
        "terminal_access": 90,
        "curb_control": 65,
        "traffic_complexity": 60,
        "pedestrian_conflict": 65,
        "staging_feasibility": 70,
        "rider_clarity": 80,
        "notes": "High passenger demand but more curb complexity."
    },
    {
        "name": "International Terminal",
        "lat": 37.6156,
        "lon": -122.3925,
        "score": 62.4,
        "category": "Complex",
        "terminal_access": 88,
        "curb_control": 55,
        "traffic_complexity": 50,
        "pedestrian_conflict": 55,
        "staging_feasibility": 60,
        "rider_clarity": 65,
        "notes": "Complex international arrivals flow."
    },
    {
        "name": "Garage G",
        "lat": 37.6206,
        "lon": -122.3907,
        "score": 86.5,
        "category": "Recommended",
        "terminal_access": 75,
        "curb_control": 92,
        "traffic_complexity": 88,
        "pedestrian_conflict": 90,
        "staging_feasibility": 95,
        "rider_clarity": 78,
        "notes": "Best AV launch candidate due to curb control and staging feasibility."
    },
]

pickup_zones = [
    apply_scenario_adjustments(zone, SCENARIO)
    for zone in pickup_zones
]

score_output = pd.DataFrame(pickup_zones)

score_output = score_output.rename(
    columns={
        "name": "zone",
        "score": "launch_score"
    }
)

score_output.to_csv(
    "outputs/sfo_zone_scores.csv",
    index=False
)

def get_zone_color(score):
    if score >= 85:
        return "green"
    elif score >= 75:
        return "orange"
    else:
        return "red"
# Add pickup markers
for zone in pickup_zones:

    color = get_zone_color(zone["score"])

    folium.CircleMarker(
        location=[zone["lat"], zone["lon"]],
        radius=13 if zone["score"] >= 85 else 10,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.75,
        popup=folium.Popup(
            f"""
            <b>{zone['name']}</b><br>
            Launch Score: {zone['score']}/100<br>
            Category: {zone['category']}<br><br>

            <b>Operational Metrics</b><br>
            Terminal Access: {zone['terminal_access']}/100<br>
            Curb Control: {zone['curb_control']}/100<br>
            Traffic Complexity: {zone['traffic_complexity']}/100<br>
            Pedestrian Conflict: {zone['pedestrian_conflict']}/100<br>
            Staging Feasibility: {zone['staging_feasibility']}/100<br>
            Rider Clarity: {zone['rider_clarity']}/100<br><br>

            <b>Notes</b><br>
            {zone['notes']}
            """,
            max_width=350,
        ),
        tooltip=f"{zone['name']} — {zone['score']}/100",
    ).add_to(m)

route_layer = folium.FeatureGroup(name="AV Routes")
# Example AV ingress routes
def get_routes(scenario):
    if scenario == "late_night":
        return [
            {
                "name": "Garage G Route",
                "color": "green",
                "risk": "Low",
                "travel_time": "3 min",
                "complexity": "Low",
                "points": [[37.6300, -122.4000], [37.6240, -122.3950], [37.6205, -122.3907]],
            },
            {
                "name": "Terminal 3 Route",
                "color": "orange",
                "risk": "Moderate",
                "travel_time": "4 min",
                "complexity": "Medium",
                "points": [[37.6300, -122.4000], [37.6215, -122.3920], [37.6192, -122.3848]],
            },
        ]

    elif scenario == "construction":
        return [
            {
                "name": "Garage G Route",
                "color": "orange",
                "risk": "Moderate",
                "travel_time": "6 min",
                "complexity": "Medium",
                "points": [[37.6300, -122.4000], [37.6240, -122.3950], [37.6205, -122.3907]],
            },
            {
                "name": "Terminal 3 Route",
                "color": "red",
                "risk": "High",
                "travel_time": "9 min",
                "complexity": "High",
                "points": [[37.6300, -122.4000], [37.6215, -122.3920], [37.6192, -122.3848]],
            },
        ]

    else:
        return [
            {
                "name": "Garage G Route",
                "color": "green",
                "risk": "Low",
                "travel_time": "4 min",
                "complexity": "Low",
                "points": [[37.6300, -122.4000], [37.6240, -122.3950], [37.6205, -122.3907]],
            },
            {
                "name": "Terminal 3 Route",
                "color": "red",
                "risk": "High",
                "travel_time": "7 min",
                "complexity": "High",
                "points": [[37.6300, -122.4000], [37.6215, -122.3920], [37.6192, -122.3848]],
            },
        ]

routes = get_routes(SCENARIO)

for route in routes:
  folium.PolyLine(
    route["points"],
    color=route["color"],
    weight=10,
    opacity=0.95,
    tooltip=(
        f"{route['name']} | "
        f"Risk: {route['risk']} | "
        f"ETA: {route['travel_time']} | "
        f"Complexity: {route['complexity']}"
    )
).add_to(route_layer)
  
  route_layer.add_to(m)
  
# Recommended zone
recommended = max(pickup_zones, key=lambda z: z["score"])

folium.Marker(
    location=[recommended["lat"], recommended["lon"]],
    tooltip="Recommended Launch Zone",
    popup=f"Recommended Zone: {recommended['name']}",
    icon=folium.Icon(icon="star"),
).add_to(m)
# Scenario-specific airport congestion layer
def get_congestion_points(scenario):
    if scenario == "peak_hour":
        return [
            [37.6156, -122.3925, 1.0],
            [37.6175, -122.3867, 0.95],
            [37.6192, -122.3848, 0.9],
            [37.6168, -122.3895, 0.95],
            [37.6183, -122.3882, 0.9],
            [37.6200, -122.3865, 0.85],
            [37.6206, -122.3907, 0.45],
        ]

    elif scenario == "late_night":
        return [
            [37.6156, -122.3925, 0.35],
            [37.6175, -122.3867, 0.25],
            [37.6192, -122.3848, 0.25],
            [37.6206, -122.3907, 0.15],
        ]

    elif scenario == "event_surge":
        return [
            [37.6156, -122.3925, 1.0],
            [37.6160, -122.3918, 1.0],
            [37.6165, -122.3908, 0.95],
            [37.6175, -122.3867, 0.9],
            [37.6192, -122.3848, 0.85],
            [37.6183, -122.3882, 0.95],
            [37.6200, -122.3865, 0.9],
        ]

    elif scenario == "construction":
        return [
            [37.6175, -122.3867, 0.9],
            [37.6178, -122.3873, 0.95],
            [37.6181, -122.3880, 1.0],
            [37.6192, -122.3848, 0.7],
            [37.6206, -122.3907, 0.4],
        ]

    else:  # normal
        return [
            [37.6156, -122.3925, 0.65],
            [37.6175, -122.3867, 0.55],
            [37.6192, -122.3848, 0.6],
            [37.6206, -122.3907, 0.25],
            [37.6168, -122.3895, 0.55],
            [37.6183, -122.3882, 0.5],
            [37.6200, -122.3865, 0.45],
        ]


congestion_points = get_congestion_points(SCENARIO)

HeatMap(
    congestion_points,
    name=f"{SCENARIO.replace('_', ' ').title()} Congestion Heatmap",
    radius=38,
    blur=30,
    min_opacity=0.3,
).add_to(m)

folium.LayerControl().add_to(m)
legend_html = f"""
<div style="
position: fixed;
bottom: 40px;
left: 40px;
width: 260px;
z-index: 9999;
background-color: white;
border: 2px solid #999;
border-radius: 8px;
padding: 12px;
font-size: 14px;
box-shadow: 2px 2px 6px rgba(0,0,0,0.25);
">
<b>SFO Launch Zone Suitability</b><br><br>
<b>Scenario:</b> {SCENARIO.replace("_", " ").title()}<br><br>

<span style="display:inline-block;width:12px;height:12px;background:green;border-radius:50%;"></span>
Recommended: 85+<br>

<span style="display:inline-block;width:12px;height:12px;background:orange;border-radius:50%;"></span>
Strong / Moderate: 75–84<br>

<span style="display:inline-block;width:12px;height:12px;background:red;border-radius:50%;"></span>
Complex: Below 75<br><br>

<b>Route Risk</b><br>

<span style="display:inline-block;width:24px;height:4px;background:green;"></span>
Low-risk AV route<br>

<span style="display:inline-block;width:24px;height:4px;background:orange;"></span>
Moderate-risk AV route<br>

<span style="display:inline-block;width:24px;height:4px;background:red;"></span>
High-risk AV route<br><br>

<b>Use case:</b><br>
AV airport pickup launch planning
</div>
"""

m.get_root().html.add_child(folium.Element(legend_html))
# Save map
output_path = os.path.join(
    OUTPUT_DIR,
    "sfo_day1_airport_map.html"
)

m.save(output_path)

print(f"Map saved to: {output_path}")
print(f"Recommended launch zone: {recommended['name']}")