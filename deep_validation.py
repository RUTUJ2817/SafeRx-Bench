import pandas as pd
import json

df = pd.read_csv('saferx-bench/scoring/scores_merged.csv')

with open('saferx-bench/data/responses/all_models.json', 'r', encoding='utf-8') as f:
    responses = {f"{r['id']}_{r['model']}": r['response'] for r in json.load(f)}

with open('saferx-bench/data/queries.json', 'r', encoding='utf-8') as f:
    queries = {q['id']: q['query'] for q in json.load(f)}

with open('saferx-bench/data/ground_truth.json', 'r', encoding='utf-8') as f:
    gt = {g['id']: g for g in json.load(f)}

# Find critical errors with hallucinations in high-risk domains
high_risk = ['pregnancy_safety', 'drug_interactions', 'renal_hepatic', 'contraindications']
candidates = df[(df['critical_error'] == 'Yes') & (df['d5'] == 'Yes') & (df['category'].isin(high_risk))]

print("=== TOP CRITICAL FAILURES ===")
# Take up to 3 candidates
for idx, row in candidates.head(3).iterrows():
    qid = row['query_id']
    model = row['model']
    resp = responses.get(f"{qid}_{model}", "N/A")
    query_text = queries.get(qid, "N/A")
    gt_info = gt.get(qid, {})
    
    print(f"Example {idx}:")
    print(f"Query: {query_text}")
    print(f"Model: {model}")
    print(f"Response: {resp[:200]}...")
    print(f"Must Not Say Violated: {gt_info.get('must_not_say', [])}")
    print(f"Key Safety Points: {gt_info.get('key_safety_points', [])}")
    print(f"Category: {row['category']}")
    print("-" * 50)
