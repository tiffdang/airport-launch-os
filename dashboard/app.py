import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os
import subprocess

st.set_page_config(
    page_title="Airport Launch OS",
    layout="wide"
)

st.title("Airport Launch OS")

st.markdown(
    """
    Autonomous Mobility Deployment Planning Platform

    This prototype simulates operational planning workflows for autonomous
    vehicle airport launches, including congestion modeling, launch zone
    scoring, ingress routing analysis, and scenario-based operational risk.
    """
)

scenario = st.sidebar.selectbox(
    "Select Scenario",
    ["normal", "peak_hour", "late_night", "event_surge", "construction"],
    index=1
)

if st.sidebar.button("Run Scenario"):
    with st.spinner("Generating scenario map..."):
        subprocess.run(
            ["python", "gis/day1_sfo_map.py", scenario],
            check=True
        )

    st.success(f"{scenario.replace('_', ' ').title()} scenario generated.")
    st.rerun()

st.sidebar.markdown("### Scenario")
st.sidebar.write(f"Current mode: **{scenario.replace('_', ' ').title()}**")
st.sidebar.markdown("### Scoring Weights")

curb_weight = st.sidebar.slider("Curb Control", 0.0, 1.0, 0.25, 0.05)
traffic_weight = st.sidebar.slider("Traffic Complexity", 0.0, 1.0, 0.25, 0.05)
staging_weight = st.sidebar.slider("Staging Feasibility", 0.0, 1.0, 0.25, 0.05)
rider_weight = st.sidebar.slider("Rider Clarity", 0.0, 1.0, 0.25, 0.05)

scores_path = "outputs/sfo_zone_scores.csv"
map_path = "outputs/sfo_day1_airport_map.html"

# KPI ROW
if os.path.exists(scores_path):
    kpi_df = pd.read_csv(scores_path)

    avg_launch_score = round(kpi_df["launch_score"].mean(), 1)
    highest_risk_zone = kpi_df.sort_values("launch_score").iloc[0]["zone"]

else:
    avg_launch_score = "N/A"
    highest_risk_zone = "N/A"

scenario_eta = {
    "normal": "5.0 min",
    "peak_hour": "7.2 min",
    "late_night": "3.8 min",
    "event_surge": "8.5 min",
    "construction": "9.0 min",
}

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Launch Feasibility Score", avg_launch_score)

with kpi2:
    st.metric("Estimated Pickup Time", scenario_eta.get(scenario, "N/A"))

with kpi3:
    st.metric("Most Constrained Zone", highest_risk_zone)

with kpi4:
    st.metric("Operating Scenario", scenario.replace("_", " ").title())

# MAIN LAYOUT
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### SFO Operational Map")

    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            map_html = f.read()

        components.html(map_html, height=620, scrolling=True)
    else:
        st.warning("Map output not found. Run `python gis/day1_sfo_map.py` first.")

with col2:
    st.markdown("### Launch Zone Scores")

    if os.path.exists(scores_path):
        df = pd.read_csv(scores_path)

        total_weight = (
            curb_weight +
            traffic_weight +
            staging_weight +
            rider_weight
        )

        df["adjusted_score"] = (
            df["curb_control"] * curb_weight +
            df["traffic_complexity"] * traffic_weight +
            df["staging_feasibility"] * staging_weight +
            df["rider_clarity"] * rider_weight
        ) / total_weight

        df["adjusted_score"] = df["adjusted_score"].round(1)

        st.dataframe(
            df[["zone", "adjusted_score", "category"]],
            use_container_width=True
        )

        top_zone = df.sort_values(
            "adjusted_score",
            ascending=False
        ).iloc[0]

        st.metric(
            label="Recommended Launch Zone",
            value=top_zone["zone"],
            delta=f"{top_zone['adjusted_score']}/100"
        )

        recommended_score = top_zone["adjusted_score"]

        if recommended_score >= 85:
            readiness = "🟢 Ready"
        elif recommended_score >= 75:
            readiness = "🟡 Conditional"
        else:
            readiness = "🔴 Not Recommended"

        st.metric("Launch Readiness", readiness)
        st.markdown("### Why This Zone?")

        zone_rationale = {
            "Garage G": [
                "Dedicated staging feasibility",
                "Lower pickup congestion exposure",
                "Direct ingress routing",
                "Operational separation from terminal congestion",
            ],
            "Terminal 2": [
                "Balanced terminal access",
                "Moderate curb control",
                "Good rider pickup clarity",
                "Useful fallback during Garage G constraints",
            ],
            "Terminal 3": [
                "Strong terminal access",
                "High passenger demand",
                "Useful when curb pressure is manageable",
                "Requires monitoring for pedestrian conflict",
            ],
            "International Terminal": [
                "High demand coverage",
                "Useful for international arrival flows",
                "Requires stronger curb management",
                "Higher operational complexity",
            ],
        }

        for reason in zone_rationale.get(top_zone["zone"], ["No rationale available"]):
                st.write(f"✓ {reason}")


        
st.markdown("### Recommended Operational Actions")

recommendations = {
    "normal": """
    - Maintain standard AV dispatch cadence
    - Monitor Terminal 3 curb utilization
    - Garage G remains primary staging area
    """,

    "peak_hour": """
    - Reduce AV dispatch density
    - Prioritize Garage G overflow staging
    - Avoid Terminal 3 congestion corridor
    """,

    "late_night": """
    - Increase AV pickup throughput
    - Utilize direct terminal routing
    - Reduced curb conflict expected
    """,

    "event_surge": """
    - Activate overflow pickup operations
    - Increase rider communication alerts
    - Deploy temporary staging support
    """,

    "construction": """
    - Reroute ingress traffic
    - Reduce curbside dwell time
    - Increase operational monitoring
    """
}

st.info(recommendations.get(scenario, "No recommendation available"))
st.markdown("### Scenario Comparison")

scenario_comparison = pd.DataFrame([
    {
        "Scenario": "Normal",
        "Best Zone": "Garage G",
        "Avg Score": 74.8,
        "Avg ETA": "5.0 min",
        "Route Risk": "Moderate"
    },
    {
        "Scenario": "Peak Hour",
        "Best Zone": "Garage G",
        "Avg Score": 66.5,
        "Avg ETA": "7.2 min",
        "Route Risk": "High"
    },
    {
        "Scenario": "Late Night",
        "Best Zone": "Garage G",
        "Avg Score": 79.5,
        "Avg ETA": "3.8 min",
        "Route Risk": "Low"
    },
    {
        "Scenario": "Event Surge",
        "Best Zone": "Garage G",
        "Avg Score": 68.0,
        "Avg ETA": "8.5 min",
        "Route Risk": "High"
    },
    {
        "Scenario": "Construction",
        "Best Zone": "Terminal 2",
        "Avg Score": 62.0,
        "Avg ETA": "9.0 min",
        "Route Risk": "High"
    }
])

st.dataframe(
    scenario_comparison,
    use_container_width=True
)

st.markdown("---")
st.markdown("### Operational Summary")

st.write(
    """
    Airport Launch OS combines geospatial intelligence, operational scoring,
    congestion simulation, and autonomous vehicle deployment planning into a
    unified operational decision-support workflow.

    The platform enables scenario-based evaluation of launch feasibility across
    airport pickup zones under varying traffic and operational conditions.
    """
)