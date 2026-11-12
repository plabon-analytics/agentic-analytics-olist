import os
from typing import Literal
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from robust_call import call_with_retry, is_transient

load_dotenv()
client = genai.Client(api_key=os.environ["LLM_API_KEY"])
model = os.environ["LLM_MODEL"]


class ParsedQuestion(BaseModel):
    intent: Literal["count", "total", "ranking", "other"]
    metric: str
    time_range: str
    needs_clarification: bool
    reason: str


system_prompt = (
    "You turn business questions about the Olist e-commerce database into fields. "
    "The database holds orders from September 2016 to October 2018. "
    "intent: count, total, ranking, or other. "
    "metric: the thing being measured, such as orders, revenue or customers. "
    "time_range: the period asked about, or 'none' if no period is given. "
    "needs_clarification: true when a metric such as revenue has more than one "
    "possible definition, or when the time period cannot be found in the data. "
    "reason: one short sentence explaining your choice."
)


def question_to_json(question):
    def make_call():
        response = client.models.generate_content(
            model=model,
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=ParsedQuestion,
            ),
        )
        if response.parsed is None:
            raise ValueError("No valid JSON came back: " + str(response.text))
        return response.parsed

    return call_with_retry(make_call, is_transient)


questions = [
    "How many orders were placed in January 2018?",
    "Show me revenue for last month",
    "Which product category sells the most?",
]

for q in questions:
    outcome = question_to_json(q)
    print(q)
    if outcome["ok"]:
        print(outcome["data"].model_dump())
    else:
        print("FAILED:", outcome["error_type"], "-", outcome["detail"])
    print("Attempts:", outcome["attempts"])
    print()