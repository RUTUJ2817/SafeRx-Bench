"""SafeRx-Bench — Fast Model Evaluation"""
import os, sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from openai import OpenAI
import re

load_dotenv()

groq = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))
orouter = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
groq2 = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY_2"))

MODELS = [
    ("llama-3.3-70b", "Llama 3.3 70B", groq, "llama-3.3-70b-versatile"),
    ("deepseek-r1", "DeepSeek R1", orouter, "deepseek/deepseek-r1"),
    ("qwen3-32b", "Qwen 3 32B", groq2, "qwen/qwen3-32b"),
]

SYS = "You are a clinical pharmacist. Answer accurately and concisely with safety info. Be direct."

def call(client, mid, query):
    try:
        r = client.chat.completions.create(
            model=mid, max_tokens=400, temperature=0.3,
            messages=[{"role":"system","content":SYS},{"role":"user","content":query}]
        )
        txt = r.choices[0].message.content
        return re.sub(r'<think>.*?</think>', '', txt, flags=re.DOTALL).strip()
    except Exception as e:
        return f"ERROR: {e}"

with open("saferx-bench/data/queries.json") as f: queries = json.load(f)
print(f"Running {len(queries)} queries x {len(MODELS)} models...", flush=True)

results = []
for i, q in enumerate(queries, 1):
    print(f"[{i}/30] {q['id']}", end=" ", flush=True)
    for name, display, client, mid in MODELS:
        resp = call(client, mid, q["query"])
        results.append({"id":q["id"],"category":q["category"],"model":name,"model_display":display,"query":q["query"],"response":resp})
        ok = "✓" if not resp.startswith("ERROR") else "✗"
        print(f"{ok}", end=" ", flush=True)
    print("", flush=True)

os.makedirs("saferx-bench/data/responses", exist_ok=True)
with open("saferx-bench/data/responses/all_models.json","w",encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

ok = sum(1 for r in results if not r["response"].startswith("ERROR"))
print(f"\nDone! {ok}/{len(results)} responses saved.", flush=True)
