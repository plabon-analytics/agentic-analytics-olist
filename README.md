# agentic-analytics-olist

A learning and research project. I am building a text-to-SQL analytics agent on the Olist e-commerce dataset, one level at a time, and measuring how well it works. The work is documented as it happens, including the mistakes.

## Status

- Week 0 (setup, database, verified schema notes, gold SQL for the dev questions): done
- Level 0 (what an agent is): done
- Level 1 (talking to a language model from Python): in progress, Lessons 1.1 to 1.4 done
- No agent exists yet. The agent loop starts at Level 2.

## Revenue has no single definition

Olist has no revenue column. I found five different totals, depending on what is counted (item price, item price plus freight, payment value, and whether canceled orders are included). The evaluation questions use payment value on delivered orders. Details are in `docs/schema_notes.md`. A key question for the agent is whether it uses a definition like this or silently guesses one.

## Roadmap

| Level | Topic | Status |
|---|---|---|
| 0 | Orientation: script, workflow and agent | Done |
| 1 | The language model as a tool | In progress |
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
- `question_to_json.py`: turns a business question into JSON fields using a schema

## Repo layout

- `src/`: code
- `docs/research_log.md`: dated notes on what I tried, what happened, and what I learned
- `docs/schema_notes.md`: verified facts about the Olist tables, keys, traps and totals
- `evals/dev_questions.csv`: 5 development questions (gold SQL for 4, a rubric for 1)
- `trajectories/`: saved agent runs (empty until Level 2)
- `data/`: not in Git, see below

## Reproduce the setup

1. Clone the repo and open a terminal in it.
2. Create the environment: `python3 -m venv .venv`, then `source .venv/bin/activate`
3. Install the packages: `pip install -r requirements.txt`
4. Download the Olist dataset from Kaggle (check its licence) and put the nine CSV files in `data/`.
5. Build the database: `python src/load_db.py`
6. Check the gold SQL: `python src/check_gold.py`. It should print 7269 for Q1, 6922900.24 for Q2, health_beauty with about 1233131.72 for Q3, and 18551 for Q4.
7. For the Level 1 scripts, copy `.env.example` to `.env` and fill in `LLM_API_KEY`, `LLM_PROVIDER` and `LLM_MODEL`. So far I use the Gemini API (Google AI Studio key). Results depend on the model, so the exact model name used is recorded in `docs/research_log.md`.

## Data and keys

The Olist data is not included in this repo. The API key lives only in `.env`, which is never committed.

## Next

Level 1, Lesson 1.5 (handling failures: broken JSON, provider errors and retries), then the Level 1 project, a function that turns a business question into clean JSON.
