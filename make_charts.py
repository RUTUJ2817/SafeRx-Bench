"""SafeRx-Bench — Research-Grade Chart Generation"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from math import pi

# Set aesthetic style
plt.style.use('dark_background')
sns.set_theme(style="darkgrid", rc={"axes.facecolor": "#161b22", "figure.facecolor": "#0d1117",
                                   "axes.edgecolor": "#30363d", "grid.color": "#30363d",
                                   "text.color": "#c9d1d9", "axes.labelcolor": "#c9d1d9",
                                   "xtick.color": "#8b949e", "ytick.color": "#8b949e"})

# Load merged scores
df = pd.read_csv('saferx-bench/scoring/scores_merged.csv')
df['d5'] = df['d5'].fillna('N/A')

os.makedirs('saferx-bench/figures', exist_ok=True)

def calc_rate(group, condition_col, condition_val='Yes'):
    return (group[condition_col] == condition_val).sum() / len(group) * 100

# --- EXISTING CHARTS ---

# 1. Error Rate by Category
cat_error = df.groupby('category').apply(lambda x: calc_rate(x, 'error_flag')).sort_values(ascending=True)
plt.figure(figsize=(10, 6))
bars = plt.barh(cat_error.index.str.replace('_', ' ').str.title(), cat_error.values, color='#922B21')
plt.xlabel('Error Rate (%)'); plt.title('Error Rate by Category', fontweight='bold')
for bar in bars:
    plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{bar.get_width():.0f}%', va='center', color='white', fontweight='bold')
plt.xlim(0, max(cat_error.values) + 15); plt.tight_layout(); plt.savefig('saferx-bench/figures/error_by_category.png', dpi=150); plt.close()

# 2. Hallucination Rate by Category
cat_hal = df.groupby('category').apply(lambda x: calc_rate(x, 'd5')).sort_values(ascending=True)
plt.figure(figsize=(10, 6))
bars = plt.barh(cat_hal.index.str.replace('_', ' ').str.title(), cat_hal.values, color='#C99114')
plt.xlabel('Hallucination Rate (%)'); plt.title('Hallucination Rate by Category', fontweight='bold')
for bar in bars:
    plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f'{bar.get_width():.0f}%', va='center', color='white', fontweight='bold')
plt.xlim(0, max(cat_hal.values) + 15 if max(cat_hal.values) > 0 else 20); plt.tight_layout(); plt.savefig('saferx-bench/figures/hallucination_by_category.png', dpi=150); plt.close()

# 3. Score Distribution
plt.figure(figsize=(8, 5))
sns.histplot(df['total'], bins=range(0, 10), color='#58a6ff', edgecolor='#30363d', discrete=True)
plt.axvline(x=5.5, color='#da3633', linestyle='--', linewidth=2)
plt.text(5.2, plt.gca().get_ylim()[1]*0.9, 'Error threshold\n(< 6)', color='#da3633', ha='right', fontweight='bold')
plt.xlabel('Total Score (0-8)'); plt.ylabel('Count'); plt.title('Score Distribution', fontweight='bold'); plt.xticks(range(0, 9))
plt.tight_layout(); plt.savefig('saferx-bench/figures/score_distribution.png', dpi=150); plt.close()

# 4. Error Rate by Model
model_error = df.groupby('model').apply(lambda x: calc_rate(x, 'error_flag')).sort_values(ascending=False)
plt.figure(figsize=(8, 6))
bars = plt.bar(model_error.index, model_error.values, color=['#58a6ff', '#f78166', '#7ee787'])
plt.ylabel('Error Rate (%)'); plt.title('Error Rate by Model', fontweight='bold')
for bar in bars:
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.0f}%', ha='center', color='white', fontweight='bold', fontsize=12)
plt.ylim(0, max(model_error.values) + 10); plt.tight_layout(); plt.savefig('saferx-bench/figures/error_by_model.png', dpi=150); plt.close()

# 5. Critical Error Rate by Model
model_crit = df.groupby('model').apply(lambda x: calc_rate(x, 'critical_error')).sort_values(ascending=False)
plt.figure(figsize=(8, 6))
bars = plt.bar(model_crit.index, model_crit.values, color=['#da3633', '#d29922', '#3fb950'])
plt.ylabel('Critical Error Rate (%)'); plt.title('Critical Error Rate by Model', fontweight='bold')
for bar in bars:
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.0f}%', ha='center', color='white', fontweight='bold', fontsize=12)
plt.ylim(0, max(model_crit.values) + 10 if max(model_crit.values) > 0 else 20); plt.tight_layout(); plt.savefig('saferx-bench/figures/critical_error_by_model.png', dpi=150); plt.close()


# --- NEW DEEP-DIVE CHARTS ---

# 6. Radar Chart of Sub-Scores (D1-D4)
plt.figure(figsize=(8, 8))
categories = ['Accuracy (D1)', 'Completeness (D2)', 'Safety (D3)', 'Clinical Reasoning (D4)']
N = len(categories)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]
ax = plt.subplot(111, polar=True)
ax.set_facecolor('#161b22')
plt.xticks(angles[:-1], categories, color='#c9d1d9', size=12, fontweight='bold')
ax.set_rlabel_position(0)
plt.yticks([0.5, 1.0, 1.5, 2.0], ["0.5", "1.0", "1.5", "2.0"], color="#8b949e", size=10)
plt.ylim(0, 2)
colors = ['#58a6ff', '#f78166', '#7ee787']
for idx, model in enumerate(df['model'].unique()):
    m_df = df[df['model'] == model]
    values = [m_df['d1'].mean(), m_df['d2'].mean(), m_df['d3'].mean(), m_df['d4'].mean()]
    values += values[:1]
    ax.plot(angles, values, linewidth=2, linestyle='solid', label=model, color=colors[idx])
    ax.fill(angles, values, color=colors[idx], alpha=0.1)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.title('Average Sub-Scores by Model (Max 2)', size=16, fontweight='bold', y=1.1)
plt.tight_layout(); plt.savefig('saferx-bench/figures/radar_subscores.png', dpi=150); plt.close()

# 7. Error Rate by Difficulty Level
diff_error = df.groupby('difficulty').apply(lambda x: calc_rate(x, 'error_flag'))
# reorder 
order = ['easy', 'moderate', 'high']
diff_error = diff_error.reindex(order)
plt.figure(figsize=(8, 6))
bars = plt.bar(diff_error.index.str.title(), diff_error.values, color='#8a2be2')
plt.ylabel('Error Rate (%)'); plt.title('Error Rate by Difficulty Level', fontweight='bold')
for bar in bars:
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.0f}%', ha='center', color='white', fontweight='bold', fontsize=12)
plt.ylim(0, max(diff_error.values) + 15 if max(diff_error.values) > 0 else 20)
plt.tight_layout(); plt.savefig('saferx-bench/figures/error_by_difficulty.png', dpi=150); plt.close()

# 8. Score Heatmap (Model vs Category)
heatmap_data = df.pivot_table(index='model', columns='category', values='total', aggfunc='mean')
heatmap_data.columns = [c.replace('_', ' ').title() for c in heatmap_data.columns]
plt.figure(figsize=(10, 5))
sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="YlGnBu_r", vmin=0, vmax=8, cbar_kws={'label': 'Avg Total Score (0-8)'})
plt.title('Average Total Score: Model vs. Category', fontweight='bold')
plt.xlabel(''); plt.ylabel('')
plt.tight_layout(); plt.savefig('saferx-bench/figures/heatmap_score.png', dpi=150); plt.close()

# 9. Stacked Bar Chart of Score Components
avg_scores = df.groupby('model')[['d1', 'd2', 'd3', 'd4']].mean()
fig, ax = plt.subplots(figsize=(8, 6))
avg_scores.plot(kind='bar', stacked=True, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'], ax=ax)
plt.title('Score Breakdown by Model (Max 8)', fontweight='bold')
plt.xlabel(''); plt.ylabel('Average Total Score Component')
plt.xticks(rotation=0)
plt.legend(['Accuracy (D1)', 'Completeness (D2)', 'Safety (D3)', 'Reasoning (D4)'], bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout(); plt.savefig('saferx-bench/figures/stacked_score_components.png', dpi=150); plt.close()

# 10. Hallucination Heatmap (Model vs Category)
hal_data = df.copy()
hal_data['hal_num'] = hal_data['d5'].apply(lambda x: 100 if x == 'Yes' else 0)
hal_heat = hal_data.pivot_table(index='model', columns='category', values='hal_num', aggfunc='mean')
hal_heat.columns = [c.replace('_', ' ').title() for c in hal_heat.columns]
plt.figure(figsize=(10, 5))
sns.heatmap(hal_heat, annot=True, fmt=".0f", cmap="Reds", vmin=0, vmax=100, cbar_kws={'label': 'Hallucination Rate (%)'})
plt.title('Hallucination Rate: Model vs. Category', fontweight='bold')
plt.xlabel(''); plt.ylabel('')
plt.tight_layout(); plt.savefig('saferx-bench/figures/heatmap_hallucination.png', dpi=150); plt.close()

print("Generated 10 high-quality dark-mode visualizations using full dataset!")
