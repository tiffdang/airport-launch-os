import pandas as pd

# Candidate pickup zones for SFO airport launch planning
pickup_zones = [
    {
        "zone": "Terminal 2",
        "terminal_access": 85,
        "curb_control": 75,
        "traffic_complexity": 65,
        "pedestrian_conflict": 70,
        "staging_feasibility": 80,
        "rider_clarity": 85,
    },
    {
        "zone": "Terminal 3",
        "terminal_access": 90,
        "curb_control": 65,
        "traffic_complexity": 60,
        "pedestrian_conflict": 65,
        "staging_feasibility": 70,
        "rider_clarity": 80,
    },
    {
        "zone": "International Terminal",
        "terminal_access": 88,
        "curb_control": 55,
        "traffic_complexity": 50,
        "pedestrian_conflict": 55,
        "staging_feasibility": 60,
        "rider_clarity": 65,
    },
    {
        "zone": "Garage G",
        "terminal_access": 75,
        "curb_control": 92,
        "traffic_complexity": 88,
        "pedestrian_conflict": 90,
        "staging_feasibility": 95,
        "rider_clarity": 78,
    },
]

# Weights reflect what matters most for an AV airport launch
weights = {
    "terminal_access": 0.20,
    "curb_control": 0.20,
    "traffic_complexity": 0.20,
    "pedestrian_conflict": 0.15,
    "staging_feasibility": 0.15,
    "rider_clarity": 0.10,
}

def calculate_launch_score(zone):
    score = 0

    for factor, weight in weights.items():
        score += zone[factor] * weight

    return round(score, 1)

for zone in pickup_zones:
    zone["launch_score"] = calculate_launch_score(zone)

df = pd.DataFrame(pickup_zones)
df = df.sort_values(by="launch_score", ascending=False)

print("\nSFO Launch Zone Scoring")
print("=======================")
print(df[["zone", "launch_score"]].to_string(index=False))

best_zone = df.iloc[0]

print("\nRecommended Launch Zone")
print("=======================")
print(f"Zone: {best_zone['zone']}")
print(f"Score: {best_zone['launch_score']}/100")

print("\nRationale")
print("=========")
print(
    f"{best_zone['zone']} ranks highest due to strong curb control, "
    "staging feasibility, and lower operational complexity for an autonomous vehicle airport launch."
)

# Save results
df.to_csv("outputs/sfo_zone_scores.csv", index=False)

print("\nSaved scoring output to outputs/sfo_zone_scores.csv")