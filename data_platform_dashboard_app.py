
import streamlit as st
import pandas as pd
import os

# Load base evaluation scores
df = pd.read_csv("Data_Platform_Evaluation_Raw.csv")

st.title("Data Governance Architecture Evaluation")

st.write("### Evaluation Matrix (Raw Scores)")
st.dataframe(df.set_index("Criteria"))

st.write("### Criteria Justifications")

criteria_files = {
    "Total Cost of Ownership (TCO)": "TCO_Justification.md",
    "Time to Deploy": "Time_to_Deploy_Justification.md",
    "Feature Completeness": "Feature_Completeness_Justification.md",
    "Customization Required": "Customization_Required_Justification.md",
    "Scalability & Extensibility": "Scalability_&_Extensibility_Justification.md",
    "Business User Experience": "Business_User_Experience_Justification.md",
    "Governance & Compliance": "Governance_&_Compliance_Justification.md",
    "Integration with AWS Ecosystem": "Integration_with_AWS_Ecosystem_Justification.md",
    "Support for Data Mesh & Products": "Support_for_Data_Mesh_&_Products_Justification.md",
    "Vendor Lock-in Risk": "Vendor_Lock-in_Risk_Justification.md",
}

for criterion, file in criteria_files.items():
    if os.path.exists(file):
        with st.expander(criterion):
            with open(file, "r") as f:
                st.markdown(f.read(), unsafe_allow_html=True)
    else:
        st.warning(f"Justification file for '{criterion}' not found.")
