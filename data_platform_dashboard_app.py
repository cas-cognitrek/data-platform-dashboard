
import streamlit as st
import pandas as pd
import re

# Static weights (baseline, from file)
static_weights = {
    'Time to Deploy': 0.10,
    'Feature Completeness': 0.15,
    'Scalability & Extensibility': 0.10,
    'Business User Experience': 0.10,
    'Governance & Compliance': 0.10,
    'Integration with AWS Ecosystem': 0.10,
    'Vendor Lock-in Risk': 0.10
}

# Dynamic weight maps
tco_weights = {
    'low': 0.20,
    'medium': 0.25,
    'high': 0.30,
    'very high': 0.40
}

custom_weights = {
    '< 160': 0.10,
    '161–480': 0.15,
    '481–1000': 0.20,
    '> 1000': 0.30
}

def normalize_key(key: str) -> str:
    return re.sub(r"[^\w<>]+", "-", key.strip())

custom_weights_normalized = {
    normalize_key(k): v for k, v in custom_weights.items()
}

def compute_weights(tco_level: str, customization_level: str):
    tco_weight = tco_weights[tco_level.strip().lower()]
    customization_weight = custom_weights_normalized[normalize_key(customization_level)]

    dynamic_total = tco_weight + customization_weight
    remaining_weight = 1.0 - dynamic_total

    static_total = sum(static_weights.values())
    scale_factor = remaining_weight / static_total

    adjusted = {
        "Total Cost of Ownership (TCO)": round(tco_weight, 4),
        "Customization Required": round(customization_weight, 4)
    }
    explanation = {
        "Total Cost of Ownership (TCO)": f"TCO level '{tco_level}' = {tco_weight:.2f}",
        "Customization Required": f"Customization level '{customization_level}' = {customization_weight:.2f}"
    }

    for k, v in static_weights.items():
        scaled = round(v * scale_factor, 4)
        adjusted[k] = scaled
        explanation[k] = f"Original {v:.2f} scaled by {scale_factor:.4f} → {scaled:.4f}"

    return pd.DataFrame([
        {"Criteria": k, "Adjusted Weight": adjusted[k], "Explanation": explanation[k]}
        for k in adjusted
    ])

# Streamlit UI
st.title("Dynamic Weighting Calculator")

tco_input = st.selectbox("Select TCO Level", list(tco_weights.keys()))
custom_input = st.selectbox("Select Customization Required (FTE Range)", list(custom_weights.keys()))

df = compute_weights(tco_input, custom_input)

st.subheader("Adjusted Weights with Explanation")
st.dataframe(df)

csv = df[["Criteria", "Adjusted Weight"]].to_csv(index=False)
st.download_button("Download weights.csv", csv, file_name="weights.csv", mime="text/csv")
