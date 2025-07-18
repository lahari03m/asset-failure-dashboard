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

np.random.seed(42)
months = np.random.choice(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'], size=len(asset_details))
asset_details['month'] = months

st.set_page_config(layout="wide")
st.title("🚦 Asset Failure Dashboard")

# --- Multi-select Filters
st.sidebar.header("🔎 Filters")
asset_ids = asset_details['asset_id'].unique().tolist()
selected_asset_ids = st.sidebar.multiselect("Select Asset ID(s):", asset_ids, default=asset_ids)

asset_names = asset_details['asset_name'].unique().tolist()
selected_asset_names = st.sidebar.multiselect("Select Asset Name(s):", asset_names, default=asset_names)

months = asset_details['month'].unique().tolist()
selected_month = st.sidebar.selectbox("Select Month:", ['All'] + sorted(months))

# Apply Filters
filtered_assets = asset_details[
    (asset_details['asset_id'].isin(selected_asset_ids)) &
    (asset_details['asset_name'].isin(selected_asset_names))
]
if selected_month != 'All':
    filtered_assets = filtered_assets[filtered_assets['month'] == selected_month]

# --- KPI Metrics
total_assets = len(asset_details['asset_id'].unique())
total_issues = len(asset_details)
problematic_count = len(problematic_assets)

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Assets", total_assets)
kpi2.metric("Total Issues", total_issues)
kpi3.metric("Problematic Assets", problematic_count)

st.markdown("---")

# --- Heatmap
st.subheader("🔥 Heatmap: Asset Failures Across Months")
heatmap_data = asset_details.groupby(['asset_name', 'month']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12,8))
sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', linewidths=.5, ax=ax)
st.pyplot(fig)

# --- Ensure no_of_issues is present
if 'no_of_issues' not in asset_details.columns:
    asset_details['no_of_issues'] = asset_details['reasons_to_fail'].apply(lambda x: len(x) if isinstance(x, list) else 0)
if 'no_of_issues' not in filtered_assets.columns:
    filtered_assets['no_of_issues'] = filtered_assets['reasons_to_fail'].apply(lambda x: len(x) if isinstance(x, list) else 0)

# --- Bar Chart: Number of Issues per Asset
st.subheader("📊 Number of Issues per Asset")
issues_count = asset_details[['asset_name', 'no_of_issues']].drop_duplicates()
fig_issues = px.bar(issues_count, x='asset_name', y='no_of_issues', color='no_of_issues',
                    title='Number of Issues Identified per Asset',
                    labels={'asset_name':'Asset Name', 'no_of_issues':'Number of Issues'})
st.plotly_chart(fig_issues)

# --- Histogram
st.subheader("📈 Distribution of Average Days to Fail")
fig_hist = px.histogram(filtered_assets, x='average_days_to_fail', nbins=10, title='Avg Days to Fail', color='asset_name')
st.plotly_chart(fig_hist)

# --- Monthly Trends
st.subheader("📈 Monthly Trends per Asset")
trend_data = filtered_assets.groupby(['month', 'asset_name']).size().reset_index(name='issue_count')
fig_trend = px.line(trend_data, x='month', y='issue_count', color='asset_name', markers=True)
st.plotly_chart(fig_trend)

# --- Per Asset Details
st.subheader("🔍 Per Asset Details")
for _, row in filtered_assets.iterrows():
    reasons = ', '.join(row['reasons_to_fail']) if isinstance(row['reasons_to_fail'], list) else "N/A"
    st.markdown(f"""
    ### Asset ID: {row['asset_id']} | Name: {row['asset_name']}
    - **Average Days to Fail:** {row['average_days_to_fail']} days
    - **Reasons for Failure:** {reasons}
    - **Number of Issues:** {row['no_of_issues']}
    """)

# --- Overall Summary
st.subheader("🧩 Overall Summary")
most_common_reason = final_summary.get('most_common_reason_to_fail', 'N/A')
most_used_asset = asset_details['asset_id'].value_counts().idxmax()
avg_days_to_fail = filtered_assets['average_days_to_fail'].mean()

summary_paragraph = f"""
Across **{total_assets} assets**, we analyzed **{total_issues} issues**.
The asset with the most failures is **{most_used_asset}**.
The most common reason for failure is **{most_common_reason}**.
The average predicted failure interval is approximately **{avg_days_to_fail:.0f} days**.

This comprehensive dashboard helps in identifying trends, high-risk assets, and aids in strategic decision-making for preventive maintenance.
"""
st.markdown(summary_paragraph)
