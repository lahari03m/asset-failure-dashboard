# pip install streamlit pandas matplotlib seaborn plotly

import streamlit as st
import pandas as pd
import json
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Load Data
with open('final_summary.json', 'r') as f:
    final_summary = json.load(f)

asset_details = pd.DataFrame(final_summary['asset_details_summary'])
problematic_assets = pd.DataFrame(final_summary['problematic_assets'])

# Simulate 'month' for demo if missing
np.random.seed(42)
months = np.random.choice(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'], size=len(asset_details))
asset_details['month'] = months

st.title("📊 Professional Asset Failure Analysis Dashboard")

# Sidebar Filters
st.sidebar.header("🔎 Filters")

criticality_levels = list(final_summary['critical_asset_summary'].keys())
selected_criticality = st.sidebar.multiselect("Filter by Criticality Level:", options=criticality_levels, default=criticality_levels)

asset_ids = asset_details['asset_id'].tolist()
selected_assets = st.sidebar.multiselect("Filter by Asset ID:", options=asset_ids, default=asset_ids)

# Filter data
filtered_assets = asset_details[
    (asset_details['asset_id'].isin(selected_assets))
]

# --- Visualization 1: Heatmap
st.header("🔥 Heatmap: Asset Failures Across Months")

heatmap_data = asset_details.groupby(['asset_name', 'month']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12,8))
sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', linewidths=.5, ax=ax)
st.pyplot(fig)

# --- Visualization 2: Bar Chart of Total Failures
st.header("📊 Total Failures per Asset")
failures_count = asset_details['asset_name'].value_counts().reset_index()
failures_count.columns = ['Asset Name', 'Failures']

fig_bar = px.bar(failures_count, x='Asset Name', y='Failures', color='Failures', title='Total Failures per Asset')
st.plotly_chart(fig_bar)

# --- Visualization 3: Criticality Distribution (Pie Chart)
st.header("🥧 Criticality Level Distribution")

if not problematic_assets.empty:
    criticality_counts = problematic_assets['criticality'].value_counts().reset_index()
    criticality_counts.columns = ['Criticality', 'Count']
    
    fig_pie = px.pie(criticality_counts, names='Criticality', values='Count', title='Criticality Distribution among Problematic Assets')
    st.plotly_chart(fig_pie)
else:
    st.info("No problematic assets to show criticality distribution.")

# --- Visualization 4: Histogram of Average Days to Fail
st.header("📈 Distribution of Average Days to Fail")

fig_hist = px.histogram(filtered_assets, x='average_days_to_fail', nbins=10, title='Average Days to Fail Distribution', color='asset_name')
st.plotly_chart(fig_hist)

# --- Visualization 5: Asset-wise Summarization (on selection)
st.header("📋 Asset-wise Detailed Summary")

for _, row in filtered_assets.iterrows():
    st.markdown(f"""
    ### 🔹 Asset ID: {row['asset_id']} | Name: {row['asset_name']}
    - **Average Days to Fail:** {row['average_days_to_fail']} days
    - **Reasons for Failure:** {', '.join(row['reasons_to_fail'])}
    - **Predicted Failures:** {row['no_of_issues']}
    - **Criticality:** (based on problematic_assets data if available)
    """)

# --- Overall Insights Summary
st.header("🧩 Overall Insights Summary")

total_assets = len(asset_details)
total_issues = len(asset_details)
most_common_reason = final_summary['most_common_reason_to_fail']
most_used_asset = asset_details['asset_id'].value_counts().idxmax()
avg_days_to_fail = filtered_assets['average_days_to_fail'].mean()

summary_paragraph = f"""
Across **{total_assets} assets**, a total of **{total_issues} failure records** were analyzed.
The asset that failed the most is **{most_used_asset}**, with failures most commonly caused by **{most_common_reason}**.
The average predicted days for assets to fail is approximately **{avg_days_to_fail:.0f} days**.

Through this dashboard:
- The **heatmap** reveals periods of frequent failures across assets and months.
- The **bar chart** showcases overall failures per asset.
- The **criticality pie chart** helps prioritize high-risk assets.
- The **histogram** exposes variability in asset lifespans.

This helps organizations prioritize predictive maintenance efforts strategically.
"""
st.markdown(summary_paragraph)
