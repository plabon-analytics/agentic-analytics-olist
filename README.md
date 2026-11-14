# agentic-analytics-olist

A learning and research project. I am building a text-to-SQL analytics agent on the Olist e-commerce dataset, one level at a time, and measuring how well it works. The work is documented as it happens, including the mistakes.

## Status

- Week 0 (setup, database, verified schema notes, gold SQL for the dev questions): done
- Level 0 (what an agent is): done
- Level 1 (talking to a language model from Python): done
- Level 2 (the agent loop, built by hand): next
- No agent exists yet. The agent loop starts at Level 2.

## Early findings

- **Revenue has no single definition.** Olist has no revenue column. I found five different totals, depending on what is counted (item price, item price plus freight, payment value, and whether canceled orders are included). The evaluation questions use payment value on delivered orders. Details are in `docs/schema_notes.md`.
- **The Level 1 translator works, and speed is the constraint.** Ten test questions all succeeded on the first attempt. Calls took between 1.8 and 179.5 seconds (median 50.7) on a free-tier Gemini model, while the visible token counts were tiny (1,788 in and 505 out for all ten calls). The cause is not measured yet.
- **A translator that reads only the words of a question cannot see traps in the data.** For example, it did not flag the difference between `customer_id` and `customer_unique_id`. That knowledge has to come from tools (Level 2) and a metrics file (Level 4).

## Roadmap

| Level | Topic | Status |
|---|---|---|
| 0 | Orientation: script, workflow and agent | Done |
| 1 | The language model as a tool | Done |
| 2 | The agent loop, built by hand | Next |
| 3 | The text-to-SQL agent | |
| 4 | Semantic layer and metric store | |
| 5 | Evaluation | |
| 6 | Frameworks and orchestration | |
| 7 | The analyst loop | |
| 8 | Production thinking | |
| 9 | Analytics-specific agents | |

## What exists so far

Scripts in `src/`:

- `load_db.py`: builds `data/olist.db` (SQLite) from the nine Olist CSV files
- `profile_db.py`: measures every table read-only and writes `data/db_profile.txt`
- `check_gold.py`: runs the gold SQL from `evals/dev_questions.csv` and prints the results
- `list_models.py`: lists the model names the API key can see
- `hello_model.py`: the first call to a language model
- `count_tokens.py`: counts tokens in sample texts
- `prompt_demo.py`: the same question with and without a system prompt
- `question_to_json.py`: an earlier version of the translator
- `robust_call.py`: retries temporary failures with growing waits and returns a clear record
- `test_retry.py`: simulates four kinds of failure without calling the API
- `translator.py`: the Level 1 function. It turns a business question into clean JSON, retries failures, and returns a record with the model, prompt version, attempts, seconds and tokens
- `run_translator_tests.py`: runs ten questions through the translator and saves each result

## Repo layout

- `src/`: code
- `docs/research_log.md`: dated notes on what I tried, what happened, and what I learned
- `docs/schema_notes.md`: verified facts about the Olist tables, keys, traps and totals
- `evals/dev_questions.csv`: 5 development questions (gold SQL for 4, a rubric for 1)
- `evals/translator_runs.csv`: one row per translator test question, with result, attempts, seconds and tokens
- `trajectories/`: saved agent runs (empty until Level 2)
- `data/`: not in Git, see below

## Reproduce the setup

1. Clone the repo and open a terminal in it.
2. Create the environment: `python3 -m venv .venv`, then `source .venv/bin/activate`
3. Install the packages: `pip install -r requirements.txt`
4. Download the Olist dataset from Kaggle (check its licence) and put the nine CSV files in `data/`.
5. Build the database: `python src/load_db.py`
6. Check the gold SQL: `python src/check_gold.py`. It should print 7269 for Q1, 6922900.24 for Q2, health_beauty with about 1233131.72 for Q3, and 18551 for Q4.
7. For the Level 1 scripts, copy `.env.example` to `.env` and fill in `LLM_API_KEY`, `LLM_PROVIDER` and `LLM_MODEL`. So far I use the Gemini API (a Google AI Studio key) with the model `gemini-3.5-flash`. Results depend on the model, so the exact model name used is recorded in `docs/research_log.md`.
8. Run the translator tests: `python src/run_translator_tests.py`. Each run appends rows to `evals/translator_runs.csv`. Free-tier providers sometimes return overload errors, which the retry helper handles.

## Data and keys

The Olist data is not included in this repo. The API key lives only in `.env`, which is never committed.

## Next

Level 2: the agent loop, built by hand without a framework. It starts with tools (Lesson 2.1): giving a model a function that it can ask for.
