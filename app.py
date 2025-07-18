# pip install streamlit pandas plotly seaborn matplotlib

import streamlit as st
import pandas as pd
import json
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Load JSON
with open('final_summary.json', 'r') as f:
    final_summary = json.load(f)

asset_details = pd.DataFrame(final_summary['asset_details_summary'])
problematic_assets = pd.DataFrame(final_summary['problematic_assets'])

# Simulate Months for Demo (replace with real data if available)
np.random.seed(42)
months = np.random.choice(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'], size=len(asset_details))
asset_details['month'] = months

st.set_page_config(layout="wide")
st.title("📊 Asset Management & Failure Analytics Dashboard")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

asset_ids = asset_details['asset_id'].unique().tolist()
selected_asset = st.sidebar.selectbox("Filter by Asset ID:", ['All'] + asset_ids)

criticality_levels = problematic_assets['criticality'].unique().tolist() if not problematic_assets.empty else []
selected_criticality = st.sidebar.selectbox("Filter by Criticality Level:", ['All'] + criticality_levels)

# Apply Filters
filtered_assets = asset_details.copy()
if selected_asset != 'All':
    filtered_assets = filtered_assets[filtered_assets['asset_id'] == selected_asset]

if selected_criticality != 'All' and not problematic_assets.empty:
    high_crit_ids = problematic_assets[problematic_assets['criticality'] == selected_criticality]['asset_no'].unique()
    filtered_assets = filtered_assets[filtered_assets['asset_id'].isin(high_crit_ids)]

# KPI Metrics
total_assets = len(asset_details['asset_id'].unique())
total_issues = len(asset_details)
problematic_count = len(problematic_assets)

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Assets", total_assets)
kpi2.metric("Total Issues", total_issues)
kpi3.metric("Problematic Assets", problematic_count)

st.markdown("---")

# Heatmap
st.subheader("🔥 Asset Failures Heatmap")
heatmap_data = asset_details.groupby(['asset_name', 'month']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12,8))
sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', linewidths=.5, ax=ax)
st.pyplot(fig)

# Bar Chart: Total Failures per Asset
st.subheader("📊 Total Failures per Asset")
failures_count = asset_details['asset_name'].value_counts().reset_index()
failures_count.columns = ['Asset Name', 'Failures']
fig_bar = px.bar(failures_count, x='Asset Name', y='Failures', color='Failures')
st.plotly_chart(fig_bar)

# Pie Chart: Criticality
st.subheader("🥧 Criticality Distribution")
if not problematic_assets.empty:
    criticality_counts = problematic_assets['criticality'].value_counts().reset_index()
    criticality_counts.columns = ['Criticality', 'Count']
    fig_pie = px.pie(criticality_counts, names='Criticality', values='Count')
    st.plotly_chart(fig_pie)
else:
    st.info("No problematic assets to show criticality distribution.")

# Histogram
st.subheader("📈 Distribution of Average Days to Fail")
fig_hist = px.histogram(filtered_assets, x='average_days_to_fail', nbins=10, title='Avg Days to Fail', color='asset_name')
st.plotly_chart(fig_hist)

# Trend Chart
st.subheader("📈 Monthly Trends per Asset")
trend_data = filtered_assets.groupby(['month', 'asset_name']).size().reset_index(name='issue_count')
fig_trend = px.line(trend_data, x='month', y='issue_count', color='asset_name', markers=True)
st.plotly_chart(fig_trend)

# Per Asset Drilldown
st.subheader("🔍 Per Asset Details")
for _, row in filtered_assets.iterrows():
    st.markdown(f"""
    ### Asset ID: {row['asset_id']} | Name: {row['asset_name']}
    - **Average Days to Fail:** {row['average_days_to_fail']} days
    - **Reasons for Failure:** {', '.join(row['reasons_to_fail'])}
    - **Number of Issues:** {row['no_of_issues']}
    """)

# Narrative Summary
st.subheader("🧩 Overall Summary")
most_common_reason = final_summary['most_common_reason_to_fail']
most_used_asset = asset_details['asset_id'].value_counts().idxmax()
avg_days_to_fail = filtered_assets['average_days_to_fail'].mean()

summary_paragraph = f"""
Across **{total_assets} assets**, we analyzed **{total_issues} issues**.
The asset with most failures: **{most_used_asset}**.
Most common reason for failure: **{most_common_reason}**.
The average predicted failure interval is approximately **{avg_days_to_fail:.0f} days**.

This dashboard enables strategic insight across assets, helping plan preventive maintenance by understanding failure trends, critical assets, and frequency across time.
"""
st.markdown(summary_paragraph)
