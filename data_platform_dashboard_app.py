
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Platform Evaluation Dashboard", layout="wide")

st.title("📊 Data Platform Evaluation Calculator")
st.markdown("Upload a CSV file with weight assignments to evaluate platform options. Total weights must sum to 100%.")

# Upload weight CSV
uploaded_file = st.file_uploader("Upload Weight Template CSV", type=["csv"])

if uploaded_file:
    weights_df = pd.read_csv(uploaded_file)
    if "Criteria" not in weights_df.columns or "Weight (%)" not in weights_df.columns:
        st.error("CSV must contain 'Criteria' and 'Weight (%)' columns.")
    else:
        if weights_df["Weight (%)"].sum() != 100:
            st.error("Total weight must equal 100% (currently %d%%)" % weights_df["Weight (%)"].sum())
        else:
            criteria = list(weights_df["Criteria"])
            weights = weights_df.set_index("Criteria")["Weight (%)"].div(100)

            # Define option scores
            options = {
                "AWS Native + Custom": [6, 4, 5, 3, 7, 4, 6, 10, 6, 9],
                "AWS + Atlan": [7, 9, 8, 9, 8, 9, 8, 7, 7, 6],
                "AWS + Collibra": [5, 6, 9, 6, 9, 7, 9, 6, 8, 5],
                "AWS + Informatica": [4, 5, 9, 5, 9, 6, 9, 5, 7, 4],
                "AWS + OpenMetadata": [8, 6, 7, 6, 8, 6, 7, 8, 6, 8],
                "AWS + DataHub": [8, 6, 6, 6, 8, 6, 6, 7, 6, 8],
                "AWS + Amundsen": [9, 5, 5, 5, 7, 6, 5, 6, 5, 9],
            }

            df_scores = pd.DataFrame(options, index=criteria)
            weighted = df_scores.mul(weights, axis=0)
            weighted.loc["Total Score"] = weighted.sum()

            st.dataframe(weighted.style.format("{:.2f}"))
            st.bar_chart(weighted.T["Total Score"].dropna())
else:
    st.info("Please upload your weight template CSV to begin.")
