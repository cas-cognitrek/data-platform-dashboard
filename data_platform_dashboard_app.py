
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Data Governance Scorecard", layout="wide")
st.title("🏗️ Data Governance Architecture Evaluation")

# Load internal raw scores
raw_scores = pd.read_csv("Data_Platform_Evaluation_Raw.csv")
criteria = raw_scores["Criteria"]
platforms = raw_scores.columns[1:]

# Dynamic weight buckets
tco_weights_map = {"low": 0.20, "medium": 0.25, "high": 0.30, "very high": 0.40}
custom_weights_map = {"low": 0.10, "medium": 0.15, "high": 0.20, "very high": 0.30}
baseline_static_weights = {
    'Time to Deploy': 0.10,
    'Feature Completeness': 0.15,
    'Scalability & Extensibility': 0.10,
    'Business User Experience': 0.10,
    'Governance & Compliance': 0.10,
    'Integration with AWS Ecosystem': 0.10,
    'Vendor Lock-in Risk': 0.10
}

# Extract TCO and Customization scores
tco_row = raw_scores[raw_scores["Criteria"] == "Total Cost of Ownership (TCO)"].iloc[0, 1:]
custom_row = raw_scores[raw_scores["Criteria"] == "Customization Required"].iloc[0, 1:]

# Bucket classification by rank
def classify_buckets(series, levels):
    ranked = series.rank(ascending=False, method="min")
    return pd.cut(ranked, bins=len(levels), labels=levels).to_dict()

tco_levels = ["very high", "high", "medium", "low"]
custom_levels = ["very high", "high", "medium", "low"]
tco_buckets = classify_buckets(tco_row, tco_levels)
custom_buckets = classify_buckets(custom_row, custom_levels)

# Calculate weighted scores per platform
weighted_scores = {}
detailed_scores = []

for platform in platforms:
    tco_level = tco_buckets[platform]
    custom_level = custom_buckets[platform]
    tco_weight = tco_weights_map[tco_level]
    custom_weight = custom_weights_map[custom_level]

    static_total = sum(baseline_static_weights.values())
    remaining_weight = 1.0 - (tco_weight + custom_weight)
    scale_factor = remaining_weight / static_total

    weights = {
        "Total Cost of Ownership (TCO)": tco_weight,
        "Customization Required": custom_weight
    }
    weights.update({k: v * scale_factor for k, v in baseline_static_weights.items()})

    total_score = 0
    row_scores = {}
    for _, row in raw_scores.iterrows():
        crit = row["Criteria"]
        score = row[platform]
        weighted = score * weights.get(crit, 0)
        row_scores[crit] = round(weighted, 2)
        total_score += weighted

    weighted_scores[platform] = round(total_score, 2)
    row_scores["Total"] = round(total_score, 2)
    row_scores["Platform"] = platform
    detailed_scores.append(row_scores)

# Build DataFrame for final display
matrix_df = pd.DataFrame(detailed_scores).set_index("Platform")
totals_df = pd.DataFrame(weighted_scores.items(), columns=["Platform", "Final Score"]).sort_values(by="Final Score", ascending=False)

# Display outputs
st.subheader("📐 Weighted Evaluation Matrix (Auto-Scored)")
st.dataframe(matrix_df)

st.subheader("📊 Final Scores by Platform")
st.dataframe(totals_df)

chart = alt.Chart(totals_df).mark_bar().encode(
    x=alt.X("Final Score:Q", title="Weighted Score"),
    y=alt.Y("Platform:N", sort='-x'),
    tooltip=["Platform", "Final Score"]
).properties(height=400)
st.altair_chart(chart, use_container_width=True)
