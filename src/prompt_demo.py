import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["LLM_API_KEY"])
model = os.environ["LLM_MODEL"]

question = "Show me revenue for last month"

system_prompt = (
    "You help analysts who query an e-commerce database called Olist. "
    "The database holds orders from September 2016 to October 2018. "
    "Read the user's business question and answer in exactly two lines. "
    "Line 1: Metric: <the metric the user asked for>. "
    "Line 2: Needs clarification: <yes or no>, then one short reason. "
    "Answer yes when a metric such as revenue has more than one possible "
    "definition, or when the time period cannot be found in the data."
)

without = client.models.generate_content(model=model, contents=question)

with_system = client.models.generate_content(
    model=model,
    contents=question,
    config=types.GenerateContentConfig(system_instruction=system_prompt),
)

print("WITHOUT a system prompt:")
print(without.text)
print("Input tokens:", without.usage_metadata.prompt_token_count)
print()
print("WITH a system prompt:")
print(with_system.text)
print("Input tokens:", with_system.usage_metadata.prompt_token_count)