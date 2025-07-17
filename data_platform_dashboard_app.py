
import streamlit as st
import pandas as pd
import os
from io import StringIO

st.title("Data Governance Architecture Evaluation")

# Upload CSV first
st.sidebar.header("Step 1: Upload Evaluation CSV")
uploaded_file = st.sidebar.file_uploader("Upload 'Data_Platform_Evaluation_Raw.csv'", type=["csv"])

if uploaded_file is not None:
    # Read uploaded CSV into DataFrame
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    df = pd.read_csv(stringio)

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
        "Vendor Lock-in Risk": "Vendor_Lock-in_Risk_Justification.md"
    }

    for criterion, file in criteria_files.items():
        if os.path.exists(file):
            with st.expander(criterion):
                with open(file, "r") as f:
                    st.markdown(f.read(), unsafe_allow_html=True)
        else:
            st.warning(f"Justification file for '{criterion}' not found.")
else:
    st.info("Please upload the evaluation CSV to begin.")
