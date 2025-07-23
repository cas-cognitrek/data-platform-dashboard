
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

st.set_page_config(page_title="Data Governance Scorecard", layout="wide")
st.title("🏗️ Data Governance Architecture Evaluation")

# Sidebar file uploader
st.sidebar.header("Upload Client Weights")
weights_file = st.sidebar.file_uploader("Upload weights.csv", type=["csv"])
if weights_file is None:
    st.warning("Please upload a weights CSV to begin.")
    st.stop()

# Load uploaded weights and convert safely
static_weights = pd.read_csv(weights_file)
static_weights["Weight"] = pd.to_numeric(static_weights["Weight"], errors="coerce")
static_weights = static_weights.dropna(subset=["Weight"])

# Load internal raw scores
raw_scores = pd.read_csv("Data_Platform_Evaluation_Raw.csv")

# Extract options
criteria = raw_scores["Criteria"]
platforms = raw_scores.columns[1:]

# Sidebar scoring method
st.sidebar.header("Scoring Configuration")
scoring_method = st.sidebar.radio("Scoring Mode", ["Linear", "Squared", "Exponential"])

# Dynamic weight mappings
tco_weights_map = {"low": 0.20, "medium": 0.25, "high": 0.30, "very high": 0.40}
custom_weights_map = {"low": 0.10, "medium": 0.15, "high": 0.20, "very high": 0.30}

# Fixed TCO and Customization level mapping (manually defined)
tco_buckets = {
    "AWS Native + Custom": "very high",
    "AWS + Amundsen": "high",
    "AWS + OpenMetadata": "high",
    "AWS + DataHub": "medium",
    "AWS + Atlan": "medium",
    "AWS + Collibra": "low",
    "AWS + Informatica": "low"
}

custom_buckets = {
    "AWS Native + Custom": "very high",
    "AWS + Amundsen": "medium",
    "AWS + OpenMetadata": "high",
    "AWS + DataHub": "high",
    "AWS + Atlan": "medium",
    "AWS + Collibra": "low",
    "AWS + Informatica": "medium"
}

# Convert to dict for lookup
baseline_static_weights = dict(zip(static_weights["Criteria"], static_weights["Weight"]))

# Prepare results
scores_df = raw_scores.copy()
final_scores = []
detailed_rows = []

for platform in platforms:
    tco_level = tco_buckets[platform]
    custom_level = custom_buckets[platform]
    tco_weight = tco_weights_map[tco_level]
    custom_weight = custom_weights_map[custom_level]

    remaining_weight = 1.0 - (tco_weight + custom_weight)
    scale_factor = remaining_weight / sum(baseline_static_weights.values())

    weights = {
        "Total Cost of Ownership (TCO)": tco_weight,
        "Customization Required": custom_weight
    }
    weights.update({k: v * scale_factor for k, v in baseline_static_weights.items()})

    platform_scores = []
    total_score = 0
    for _, row in raw_scores.iterrows():
        crit = row["Criteria"]
        raw = row[platform]
        weight = weights.get(crit, 0)
        if scoring_method == "Linear":
            val = raw * weight
        elif scoring_method == "Squared":
            val = (raw ** 2) * weight
        elif scoring_method == "Exponential":
            val = (raw ** 2.5) * weight
        total_score += val
        platform_scores.append(round(val, 2))

    scores_df[platform] = platform_scores
    final_scores.append((platform, round(total_score, 2)))
    detailed_rows.append({
        "Platform": platform,
        "TCO Level": tco_level,
        "TCO Weight": tco_weight,
        "Customization Level": custom_level,
        "Customization Weight": custom_weight,
        "Total Score": round(total_score, 2)
    })

# Display matrix
st.subheader(f"📐 Weighted Evaluation Matrix ({scoring_method})")
st.dataframe(scores_df.set_index("Criteria"))

# Display final scores
total_df = pd.DataFrame(final_scores, columns=["Platform", "Final Score"]).sort_values(by="Final Score", ascending=False)
st.subheader("📊 Final Scores by Platform")
st.dataframe(total_df)

# Chart
chart = alt.Chart(total_df).mark_bar().encode(
    x=alt.X("Final Score:Q", title="Weighted Score"),
    y=alt.Y("Platform:N", sort='-x'),
    tooltip=["Platform", "Final Score"]
).properties(height=400)
st.altair_chart(chart, use_container_width=True)

# Optional: show dynamic weight assignments
with st.expander("🔍 Dynamic Weight Details"):
    st.dataframe(pd.DataFrame(detailed_rows).set_index("Platform"))
