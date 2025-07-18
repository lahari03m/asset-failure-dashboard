# ✅ Install requirements if needed
# pip install streamlit pandas matplotlib seaborn wordcloud

import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# ✅ Load final_summary.json
with open('final_summary.json', 'r') as f:
    final_summary = json.load(f)

st.title("📊 Interactive Asset Failure Analysis Dashboard")

asset_details = pd.DataFrame(final_summary['asset_details_summary'])

# ✅ Filters
st.sidebar.header("🔎 Filters")
criticality_levels = list(final_summary['critical_asset_summary'].keys())
selected_criticality = st.sidebar.multiselect(
    "Select Criticality Levels", 
    options=criticality_levels,
    default=criticality_levels
)

asset_ids = asset_details['asset_id'].tolist()
selected_assets = st.sidebar.multiselect(
    "Select Asset IDs", 
    options=asset_ids,
    default=asset_ids
)

# ✅ Filter Data
problematic_assets_df = pd.DataFrame(final_summary['problematic_assets'])
filtered_df = asset_details[
    asset_details['asset_id'].isin(selected_assets)
]

if selected_criticality:
    filtered_df = filtered_df[filtered_df['asset_id'].isin(
        problematic_assets_df[problematic_assets_df['criticality'].isin(selected_criticality)]['asset_no']
    ) | ~problematic_assets_df['criticality'].isin(selected_criticality)]

st.header("📋 Filtered Asset Details")
st.dataframe(filtered_df)

# ✅ Visualization: Criticality Level Distribution
st.header("1. Criticality Level Distribution (Filtered)")
filtered_criticality_counts = problematic_assets_df[
    problematic_assets_df['criticality'].isin(selected_criticality)
]['criticality'].value_counts()

fig, ax = plt.subplots()
sns.barplot(x=filtered_criticality_counts.index, y=filtered_criticality_counts.values, palette='viridis', ax=ax)
ax.set_title('Assets by Criticality (Filtered)')
st.pyplot(fig)

# ✅ Visualization: Average Days to Fail
st.header("2. Average Days to Fail per Asset")
fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(data=filtered_df, x='asset_id', y='average_days_to_fail', palette='coolwarm', ax=ax)
plt.xticks(rotation=45)
ax.set_ylabel('Average Days to Fail')
st.pyplot(fig)

# ✅ Word Cloud of Reasons to Fail
st.header("3. Reasons to Fail Word Cloud")

all_reasons = []
for reasons in filtered_df['reasons_to_fail']:
    all_reasons.extend(reasons)

if all_reasons:
    reasons_text = ' '.join(all_reasons)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(reasons_text)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
else:
    st.info("No reasons found for current filter selection.")

# ✅ Most Common Reason
st.header("4. Most Common Reason to Fail Overall")
st.success(f"🔍 {final_summary['most_common_reason_to_fail']}")

st.markdown("---")
st.markdown("Developed for Interactive Asset Failure Summarization 🚀")
