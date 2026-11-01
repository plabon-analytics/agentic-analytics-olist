import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.environ["LLM_API_KEY"])

response = client.models.generate_content(
    model=os.environ["LLM_MODEL"],
    contents="In one sentence, what is an e-commerce order?",
)

print(response.text)