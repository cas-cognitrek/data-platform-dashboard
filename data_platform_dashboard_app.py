
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

st.set_page_config(page_title="Data Governance Scorecard", layout="wide")
st.title("🏗️ Data Governance Architecture Evaluation")

# Load internal raw scores
raw_scores = pd.read_csv("Data_Platform_Evaluation_Raw.csv")
criteria = raw_scores["Criteria"]
platforms = raw_scores.columns[1:]

# Sidebar: scoring mode and weights upload
st.sidebar.header("Configure Evaluation")
scoring_method = st.sidebar.radio("Scoring Mode", ["Linear", "Squared", "Exponential"])
uploaded_weights = st.sidebar.file_uploader("Upload weights.csv", type=["csv"])

if uploaded_weights:
    weights_df = pd.read_csv(uploaded_weights)
    weights_df = weights_df.set_index("Criteria").reindex(criteria)

    if weights_df.isnull().values.any():
        st.error("Weight file is missing some criteria. Please check the file.")
    else:
        st.success("Weights uploaded successfully.")

        # Apply scoring based on method
        scores_df = raw_scores.copy()
        if scoring_method == "Linear":
            for platform in platforms:
                scores_df[platform] = scores_df[platform] * weights_df["Weight"].values
        elif scoring_method == "Squared":
            for platform in platforms:
                scores_df[platform] = (scores_df[platform] ** 2) * weights_df["Weight"].values
        elif scoring_method == "Exponential":
            for platform in platforms:
                scores_df[platform] = (scores_df[platform] ** 2.5) * weights_df["Weight"].values

        totals = scores_df[platforms].sum().sort_values(ascending=False)
        total_df = totals.reset_index()
        total_df.columns = ["Platform", "Final Score"]

        st.subheader(f"{scoring_method} Weighted Scores")
        st.dataframe(scores_df.set_index("Criteria"))

        st.subheader("📊 Final Scores by Platform")
        st.dataframe(total_df)

        chart = alt.Chart(total_df).mark_bar().encode(
            x=alt.X("Final Score:Q", title="Weighted Score"),
            y=alt.Y("Platform:N", sort='-x'),
            tooltip=["Platform", "Final Score"]
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
else:
    st.info("Please upload a weights CSV to begin.")
