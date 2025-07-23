
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

st.set_page_config(page_title="Data Governance Scorecard", layout="wide")
st.title("🏗️ Data Governance Architecture Evaluation")

# Load internal files
raw_scores = pd.read_csv("Data_Platform_Evaluation_Raw.csv")
static_weights = pd.read_csv("weights_static_rescaled.csv")

# Extract inputs
criteria = raw_scores["Criteria"]
platforms = raw_scores.columns[1:]

# Sidebar: scoring method
st.sidebar.header("Configure Evaluation")
scoring_method = st.sidebar.radio("Scoring Mode", ["Linear", "Squared", "Exponential"])

# Define dynamic weight maps
tco_weights_map = {"low": 0.20, "medium": 0.25, "high": 0.30, "very high": 0.40}
custom_weights_map = {"low": 0.10, "medium": 0.15, "high": 0.20, "very high": 0.30}

# Parse raw rows
tco_row = raw_scores[raw_scores["Criteria"] == "Total Cost of Ownership (TCO)"].iloc[0, 1:]
custom_row = raw_scores[raw_scores["Criteria"] == "Customization Required"].iloc[0, 1:]

# Assign levels using ranked binning
def classify_buckets(series, levels):
    ranked = series.rank(ascending=False, method="min")
    return pd.cut(ranked, bins=len(levels), labels=levels).to_dict()

tco_levels = ["very high", "high", "medium", "low"]
custom_levels = ["very high", "high", "medium", "low"]
tco_buckets = classify_buckets(tco_row, tco_levels)
custom_buckets = classify_buckets(custom_row, custom_levels)


# Convert weight column to float safely
static_weights["Weight"] = pd.to_numeric(static_weights["Weight"], errors="coerce")
static_weights = static_weights.dropna(subset=["Weight"])

# Build baseline weight dict from file

baseline_static_weights = dict(zip(static_weights["Criteria"], static_weights["Weight"]))

# Calculate per-option scores
scores_df = raw_scores.copy()
final_scores = []
detailed_rows = []

for platform in platforms:
    # Get dynamic weights
    tco_level = tco_buckets[platform]
    custom_level = custom_buckets[platform]
    tco_weight = tco_weights_map[tco_level]
    custom_weight = custom_weights_map[custom_level]

    remaining_weight = 1.0 - (tco_weight + custom_weight)
    static_total = sum(baseline_static_weights.values())
    scale_factor = remaining_weight / static_total

    # Final weights
    weights = {
        "Total Cost of Ownership (TCO)": tco_weight,
        "Customization Required": custom_weight
    }
    weights.update({k: v * scale_factor for k, v in baseline_static_weights.items()})

    # Compute weighted score
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

# Display results
st.subheader(f"📐 Weighted Evaluation Matrix ({scoring_method})")
st.dataframe(scores_df.set_index("Criteria"))

total_df = pd.DataFrame(final_scores, columns=["Platform", "Final Score"]).sort_values(by="Final Score", ascending=False)
st.subheader("📊 Final Scores by Platform")
st.dataframe(total_df)

chart = alt.Chart(total_df).mark_bar().encode(
    x=alt.X("Final Score:Q", title="Weighted Score"),
    y=alt.Y("Platform:N", sort='-x'),
    tooltip=["Platform", "Final Score"]
).properties(height=400)
st.altair_chart(chart, use_container_width=True)

# Optional: Show dynamic weight details
with st.expander("🔍 Dynamic Weight Details"):
    st.dataframe(pd.DataFrame(detailed_rows).set_index("Platform"))
