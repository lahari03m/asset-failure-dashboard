# pip install streamlit pandas json

import streamlit as st
import pandas as pd
import json

# Load JSON
with open('final_summary.json', 'r') as f:
    final_summary = json.load(f)

asset_details = pd.DataFrame(final_summary['asset_details_summary'])
problematic_assets = pd.DataFrame(final_summary['problematic_assets'])

st.title("🔍 Asset & Criticality Classification Dashboard")

# Dropdown Filters
asset_ids = asset_details['asset_id'].unique().tolist()
selected_asset = st.selectbox("Select Asset ID:", ['All'] + asset_ids)

criticality_levels = problematic_assets['criticality'].unique().tolist() if not problematic_assets.empty else []
selected_criticality = st.selectbox("Select Criticality Level:", ['All'] + criticality_levels)

# Filtering
filtered_data = asset_details.copy()

if selected_asset != 'All':
    filtered_data = filtered_data[filtered_data['asset_id'] == selected_asset]

if selected_criticality != 'All' and not problematic_assets.empty:
    high_crit_ids = problematic_assets[problematic_assets['criticality'] == selected_criticality]['asset_no'].unique()
    filtered_data = filtered_data[filtered_data['asset_id'].isin(high_crit_ids)]

# Display Filtered Data
if not filtered_data.empty:
    st.subheader("📋 Filtered Asset Data")
    st.dataframe(filtered_data[['asset_id', 'asset_name', 'average_days_to_fail', 'reasons_to_fail', 'no_of_issues']])

    # Per Asset Summary
    st.subheader("📌 Per Asset Summary")
    for _, row in filtered_data.iterrows():
        st.markdown(f"""
        ### Asset ID: {row['asset_id']} | Name: {row['asset_name']}
        - **Average Days to Fail:** {row['average_days_to_fail']} days
        - **Reasons for Failure:** {', '.join(row['reasons_to_fail'])}
        - **Number of Issues:** {row['no_of_issues']}
        """)
else:
    st.warning("No data matches the selected filters.")
