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
    st.metric("Avg Launch Score", avg_launch_score)

with kpi2:
    st.metric("Avg ETA", scenario_eta.get(scenario, "N/A"))

with kpi3:
    st.metric("Highest Risk Zone", highest_risk_zone)

with kpi4:
    st.metric("Congestion Level", scenario.replace("_", " ").title())

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

        st.dataframe(
    df[["zone", "launch_score", "category"]],
    use_container_width=True
)

        top_zone = df.sort_values(
            "launch_score",
            ascending=False
        ).iloc[0]

        st.metric(
            label="Recommended Launch Zone",
            value=top_zone["zone"],
            delta=f"{top_zone['launch_score']}/100"
        )
        
    else:
        st.warning(
            "Score output not found. Run `python scoring/zone_scoring.py` first."
        )
st.markdown("### Operational Recommendation")

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