import pandas as pd
import json

# Load scores
scores_df = pd.read_csv('saferx-bench/scoring/scores.csv')

# Load queries to get category and difficulty
with open('saferx-bench/data/queries.json', 'r', encoding='utf-8') as f:
    queries = json.load(f)

# Create mappings from query_id to category and difficulty
category_map = {q['id']: q['category'] for q in queries}
difficulty_map = {q['id']: q.get('difficulty', 'moderate') for q in queries}

# Add columns
scores_df['category'] = scores_df['query_id'].map(category_map)
scores_df['difficulty'] = scores_df['query_id'].map(difficulty_map)

# Add critical_error column
# Critical error is defined as hallucination = Yes OR total score < 4 (very poor safety and accuracy)
scores_df['critical_error'] = scores_df.apply(lambda row: 'Yes' if row['d5'] == 'Yes' or row['total'] < 4 else 'No', axis=1)

# Save merged dataset
scores_df.to_csv('saferx-bench/scoring/scores_merged.csv', index=False)

# Verification
print("=== PREP DATA VERIFICATION ===")
print(f"Total rows: {len(scores_df)}")
print(f"Queries present: {scores_df['query_id'].nunique()} / 30")
print(f"Models present: {scores_df['model'].nunique()} / 3")
print("Sample:")
print(scores_df.head(3))
