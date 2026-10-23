# agentic-analytics-olist

A learning and research project: build a text-to-SQL analytics agent on the Olist e-commerce dataset, one level at a time, and measure how well it works.

## Status

Week 0 done. Olist is loaded into SQLite (9 tables, 99,441 orders). No agent yet.

## Open question

How should revenue be defined for Olist: item price, price plus freight, or payment value? See docs/research_log.md.

## Layout

- src/ : code
- trajectories/ : saved agent runs
- evals/ : question sets (dev_questions.csv so far, 5 questions)
- docs/research_log.md : dated notes on what I tried and learned
- data/ : not in Git, see below

## Reproduce the setup

1. Clone the repo and open a terminal in it.
2. Create the environment: python3 -m venv .venv, then source .venv/bin/activate
3. Install packages: pip install -r requirements.txt
4. Download the Olist dataset from Kaggle (check its licence) and put the 9 CSV files in data/
5. Build the database: python src/load_db.py

## Roadmap

L0 orientation, L1 LLM as a tool, L2 agent loop, L3 text-to-SQL agent, L4 semantic layer and metric store, L5 evaluation, L6 frameworks and MCP, L7 analyst loop, L8 production, L9 analytics-specific agents.

Next: L0 definition, then the L1 question-to-JSON translator.
