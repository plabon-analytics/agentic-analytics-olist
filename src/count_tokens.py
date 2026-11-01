import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["LLM_API_KEY"])
model = os.environ["LLM_MODEL"]

samples = {
    "a short sentence": "How many orders were placed in January 2018?",
    "an order_id": "e481f51cbdc54678b7cc49136f2d6af7",
    "a SQL query": "SELECT COUNT(*) FROM orders WHERE order_purchase_timestamp >= '2018-01-01' AND order_purchase_timestamp < '2018-02-01';",
    "my schema notes file": Path("docs/schema_notes.md").read_text(encoding="utf-8"),
}

for label, text in samples.items():
    result = client.models.count_tokens(model=model, contents=text)
    print(f"{label}: {len(text)} characters, {result.total_tokens} tokens")