"""SafeRx-Bench — Research-Grade Chart Generation"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set aesthetic style
plt.style.use('dark_background')
sns.set_theme(style="darkgrid", rc={"axes.facecolor": "#161b22", "figure.facecolor": "#0d1117",
                                   "axes.edgecolor": "#30363d", "grid.color": "#30363d",
                                   "text.color": "#c9d1d9", "axes.labelcolor": "#c9d1d9",
                                   "xtick.color": "#8b949e", "ytick.color": "#8b949e"})

# Load merged scores
df = pd.read_csv('saferx-bench/scoring/scores_merged.csv')

# Handle N/A in d5
df['d5'] = df['d5'].fillna('N/A')

os.makedirs('saferx-bench/figures', exist_ok=True)

# Helper for percentage
def calc_rate(group, condition_col, condition_val='Yes'):
    return (group[condition_col] == condition_val).sum() / len(group) * 100

# --- CHART 1: Error Rate by Category ---
cat_error = df.groupby('category').apply(lambda x: calc_rate(x, 'error_flag')).sort_values(ascending=True)
plt.figure(figsize=(10, 6))
bars = plt.barh(cat_error.index.str.replace('_', ' ').str.title(), cat_error.values, color='#922B21')
plt.xlabel('Error Rate (%)')
plt.title('Error Rate by Category', fontweight='bold')
for bar in bars:
    plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{bar.get_width():.0f}%', 
             va='center', color='white', fontweight='bold')
plt.xlim(0, max(cat_error.values) + 15)
plt.tight_layout()
plt.savefig('saferx-bench/figures/error_by_category.png', dpi=150)
plt.close()

# --- CHART 2: Hallucination Rate by Category ---
cat_hal = df.groupby('category').apply(lambda x: calc_rate(x, 'd5')).sort_values(ascending=True)
plt.figure(figsize=(10, 6))
bars = plt.barh(cat_hal.index.str.replace('_', ' ').str.title(), cat_hal.values, color='#C99114')
plt.xlabel('Hallucination Rate (%)')
plt.title('Hallucination Rate by Category', fontweight='bold')
for bar in bars:
    plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f'{bar.get_width():.0f}%', 
             va='center', color='white', fontweight='bold')
plt.xlim(0, max(cat_hal.values) + 15 if max(cat_hal.values) > 0 else 20)
plt.tight_layout()
plt.savefig('saferx-bench/figures/hallucination_by_category.png', dpi=150)
plt.close()

# --- CHART 3: Score Distribution ---
plt.figure(figsize=(8, 5))
sns.histplot(df['total'], bins=range(0, 10), color='#58a6ff', edgecolor='#30363d', discrete=True)
plt.axvline(x=5.5, color='#da3633', linestyle='--', linewidth=2)
plt.text(5.2, plt.gca().get_ylim()[1]*0.9, 'Error threshold\n(< 6)', color='#da3633', ha='right', fontweight='bold')
plt.xlabel('Total Score (0-8)')
plt.ylabel('Count')
plt.title('Score Distribution', fontweight='bold')
plt.xticks(range(0, 9))
plt.tight_layout()
plt.savefig('saferx-bench/figures/score_distribution.png', dpi=150)
plt.close()

# --- CHART 4: Error Rate by Model ---
model_error = df.groupby('model').apply(lambda x: calc_rate(x, 'error_flag')).sort_values(ascending=False)
plt.figure(figsize=(8, 6))
bars = plt.bar(model_error.index, model_error.values, color=['#58a6ff', '#f78166', '#7ee787'])
plt.ylabel('Error Rate (%)')
plt.title('Error Rate by Model', fontweight='bold')
for bar in bars:
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.0f}%', 
             ha='center', color='white', fontweight='bold', fontsize=12)
plt.ylim(0, max(model_error.values) + 10)
plt.tight_layout()
plt.savefig('saferx-bench/figures/error_by_model.png', dpi=150)
plt.close()

# --- CHART 5: Critical Error Rate by Model ---
model_crit = df.groupby('model').apply(lambda x: calc_rate(x, 'critical_error')).sort_values(ascending=False)
plt.figure(figsize=(8, 6))
bars = plt.bar(model_crit.index, model_crit.values, color=['#da3633', '#d29922', '#3fb950'])
plt.ylabel('Critical Error Rate (%)')
plt.title('Critical Error Rate by Model', fontweight='bold')
for bar in bars:
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{bar.get_height():.0f}%', 
             ha='center', color='white', fontweight='bold', fontsize=12)
plt.ylim(0, max(model_crit.values) + 10 if max(model_crit.values) > 0 else 20)
plt.tight_layout()
plt.savefig('saferx-bench/figures/critical_error_by_model.png', dpi=150)
plt.close()

# --- PRINT FINAL METRICS ---
total_queries = df['query_id'].nunique()
total_resp = len(df)
ov_err = calc_rate(df, 'error_flag')
ov_hal = calc_rate(df, 'd5')
ov_crit = calc_rate(df, 'critical_error')

print("\n=== FINAL RESULTS ===")
print(f"Total queries: {total_queries}")
print(f"Total responses: {total_resp}\n")
print(f"Overall error rate: {ov_err:.0f}%")
print(f"Overall hallucination rate: {ov_hal:.0f}%")
print(f"Overall critical error rate: {ov_crit:.0f}%\n")
print("Per model:\n")

for m in df['model'].unique():
    m_df = df[df['model'] == m]
    print(f"{m.capitalize()}:")
    print(f" * error: {calc_rate(m_df, 'error_flag'):.0f}%")
    print(f" * hallucination: {calc_rate(m_df, 'd5'):.0f}%")
    print(f" * critical: {calc_rate(m_df, 'critical_error'):.0f}%\n")

print("All 5 charts successfully generated in saferx-bench/figures/")
