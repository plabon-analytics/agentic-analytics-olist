import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["LLM_API_KEY"])
model = os.environ["LLM_MODEL"]

get_schema = types.FunctionDeclaration(
    name="get_schema",
    description=(
        "Returns the tables and columns of the Olist database. "
        "Call this before writing any SQL."
    ),
)

run_sql = types.FunctionDeclaration(
    name="run_sql",
    description="Runs one read-only SQLite query on the Olist database and returns the rows.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(
                type=types.Type.STRING,
                description="One SQLite SELECT statement.",
            )
        },
        required=["query"],
    ),
)

config = types.GenerateContentConfig(
    system_instruction=(
        "You answer questions about the Olist e-commerce database. "
        "Use the tools to look at the data. Never guess numbers. "
        "If a question is general and does not need the database, "
        "answer it directly without calling a tool."
    ),
    tools=[types.Tool(function_declarations=[get_schema, run_sql])],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

questions = [
    "How many sellers are there?",
    "What is a primary key in a database?",
]

for question in questions:
    started = time.perf_counter()
    response = client.models.generate_content(model=model, contents=question, config=config)
    seconds = round(time.perf_counter() - started, 1)
    print(question)
    if response.function_calls:
        for call in response.function_calls:
            print("  The model asks for a tool:", call.name, dict(call.args or {}))
    else:
        print("  The model answers directly:", response.text)
    usage = response.usage_metadata
    print(
        "  seconds:", seconds,
        "| input tokens:", usage.prompt_token_count,
        "| thinking tokens:", usage.thoughts_token_count,
    )
    print()