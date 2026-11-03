# Research log

Rule: before running a command, write its purpose here in one line. The command purposes in the two Week 0 entries were written afterward, from memory. From Week 1 on they are written before running.

## 2026-10-24 (Week 0: setup)

Purpose: get a clean, repeatable base before building any agent.

Tried: created the repo agentic-analytics-olist, downloaded Olist from Kaggle (9 CSVs), and loaded them into SQLite (data/olist.db) with the loader script in src/.

Commands and purpose:
- `python3 -m venv .venv` and `source .venv/bin/activate`: make a private box of packages for this project, so other projects cannot break it.
- `pip install pandas python-dotenv` and `pip freeze > requirements.txt`: install the tools, then write down the exact versions so the setup can be rebuilt.
- `git init`: start saving a history of every change.
- `.gitignore` and `.env`: keep secrets, the big dataset and rebuildable files out of GitHub.
- The loader script: build olist.db from the CSVs, so the data can be queried with SQL and rebuilt at any time.
- `.tables`, `SELECT * FROM orders LIMIT 5` and `SELECT COUNT(*) FROM orders`: prove the load worked before building on it.
- `git status` before committing: check that no secret or large file is about to be uploaded.
- `git commit` and `git push`: save a snapshot and put a copy on GitHub.

Happened:
- Loaded 9 tables: orders 99,441 rows, order_items 112,650, order_payments 103,886, customers 99,441, products 32,951, sellers 3,095, plus reviews, geolocation and the category translation table.
- First query failed: SELECT * FROM orders_payments. The real name is order_payments.
- Pushed the first commit to a public GitHub repo. Checked first that .env and data/ were not included.

Learned:
- Revenue is not one number. The definition changes the answer, which is the reason for the semantic layer (L4).
- pandas created the tables without primary or foreign keys, so relationships have to be checked by hand.

Ideas to test later (not learned yet):
- get_schema() may work better with row counts and a few sample values. Compare with and without in L2/L3.

Next: measure the database properly and write down verified facts.

## 2026-10-25 (Week 0: schema check and notes)

Purpose: measure the database so every later claim, and every answer the agent gives, can be checked against facts.

Tried: wrote src/profile_db.py, which opens the database read-only and measures every table. Ran it, saved the output to data/db_profile.txt, and wrote docs/schema_notes.md from it. Then ran a join experiment to see how a careless join inflates revenue.

Commands and purpose:
- `python src/profile_db.py`: measure every table in one read-only pass, so facts come from queries and not from memory.
- COUNT(*) next to COUNT(DISTINCT column): test whether a column can work as a key.
- NOT IN and LEFT JOIN checks: find rows that point to something missing (orphans).
- GROUP BY order_id with HAVING COUNT(*) > 1: find orders that have more than one payment row.
- The wrong join (items joined directly to payments): show how much a careless join inflates revenue.
- The right query (payments reduced to one row per order first): confirm the fix gives the measured total of 15,846,280.17.

Happened:
- order_payments: 103,886 rows for 99,440 orders; 2,961 orders have more than one payment row.
- Revenue totals: price 13,591,643.70 | price + freight 15,843,553.24 | payment_value 16,008,872.12.
- customers: 99,441 rows, 96,096 people; 2,997 people have more than one customer_id.
- Data is dense from 2017-01 to 2018-08. 2018-09 has 16 orders, 2018-10 has 4.
- 162,591.95 of the payment total belongs to 775 orders that have no item rows.
- Join experiment:
  - Joining order_items directly to order_payments and summing payment_value gave 20,308,134.71.
  - Reducing payments to one row per order first, for orders that have items, gave 15,846,280.17. This matches the profile exactly.
  - Difference: 4,461,854.54, about 28% too high.

Learned:
- Joining two tables that both have many rows per order multiplies rows. An order with 3 items and 1 payment of 90 sums to 270. Fix: reduce one side to one row per order before the join.
- customer_id is created for every order, so counting it counts orders. customer_unique_id counts people.
- My first notes said 3,345 repeat buyers. That number counts extra orders, not people. The real number of people with more than one customer_id is 2,997.
- I guessed vouchers caused the gap between payments and price + freight. The data says the orders without item rows did.
- Raw CSVs in data/ are inputs and are never edited. olist.db and db_profile.txt are rebuilt by scripts. .env holds the API key and never goes to Git.
- Read-only mode protects the database even if a script has a bug.

Ideas to test later (not learned yet):
- Is (order_id, payment_sequential) unique in order_payments?
- How many payment rows have 0 installments?

Eval notes: 5 draft dev questions are in evals/dev_questions.csv. None has been run, since no agent exists. Their difficulty is expected, not observed.

Details: docs/schema_notes.md

Next: write the revenue decisions and gold SQL for Q2 to Q4.

## 2026-10-26 (Week 0: gold SQL)

Purpose: write the answer key (gold SQL) the agent will later be graded against, so every grade rests on a query I understand and have checked.

Decisions (written before the SQL):
- Q2 revenue: payment_value, delivered orders only, purchase date in 2017.
- Q3 category revenue: item price, delivered orders only. Payments are not used because they cannot be split by category and would multiply rows. Products with no category show as unknown; products with no translation show the Portuguese name.
- Q4 customers: people (customer_unique_id), all order statuses, window 2018-05-03 up to but not including 2018-08-01.

Commands and purpose:
- Yearly delivered revenue by purchase year: prove the Q2 filter by adding the years up to the known delivered total.
- SUM(price) for delivered orders: get the reference total that all Q3 category totals must add up to.
- Orders, delivered orders and people in the Q4 window: see what the status filter costs and check that people never exceed orders.
- `python src/check_gold.py`: run each gold query exactly as saved in the CSV and compare with the recorded result.

Happened:
- Q2 check: 2016 = 46,586.33, 2017 = 6,922,900.24, 2018 = 8,452,975.20. Together 15,422,461.77, which equals the delivered payment total in the schema notes. Q2 is proven.
- Delivered item price total: 13,221,498.11.
- Q4 window: 18,780 orders, 18,468 of them delivered, 18,551 people (any status). Delivered-only people were 18,248.
- check_gold.py: Q1 7,269 | Q2 6,922,900.24 | Q3 health_beauty 1,233,131.72 | Q4 18,551. All four match the recorded results. Committed as bb40c0a.

Learned:
- A gold query must do what the written decision says. My first Q3 used an inner join to the translation table, which silently drops products with no category or no translation. A LEFT JOIN with COALESCE keeps them.
- The question text and the SQL must say the same thing. My first Q4 question said "placed an order" but the SQL kept only delivered orders. The agent sees the question and never sees my notes.
- A -- comment inside a CSV cell can swallow the rest of the query. Results and decisions go in the notes column.
- Changing the Q3 inner join to a LEFT JOIN did not change the top category (health_beauty). How much revenue the inner join lost is still unmeasured.
- The word "revenue" in Q2 is undefined on purpose. The metric file at L4 will supply the definition, and the gap between L3 and L4 answers is the experiment.

Ideas to test later (not learned yet):
- How much revenue the inner join in my first Q3 query lost.
- Whether the second-place category is close enough to health_beauty that a different revenue definition flips the winner.

Eval notes: dev_questions.csv has 5 questions with gold SQL for Q1 to Q4 and a rubric for Q5. All four gold queries were run with check_gold.py and match the recorded results. None of the questions has been run on an agent, since no agent exists.

Next: start the Level 0 lesson.

## 2026-10-31 (Level 0: what is an agent)

Purpose: write my own definition of an agent before I build one. Lessons 0.1 to 0.5 are done. No commands were run; Level 0 is concepts only.

Q1. In my own words, what is an agent?
An agent is like an intern who has keys to the database. I give it a question in English. The model decides what it needs and asks for a tool: get_schema() lists the tables and columns, and run_sql() runs a query. My program runs the tool and sends the result back, and the model decides the next step. This repeats until the model has an answer or my program stops it at MAX_STEPS. An agent can fix a mistake only when it gets a signal, like an error message. My inflated revenue of 20,308,134.71 ran without any error, so an agent would have reported it as if it were right. A script cannot choose its next step. It only runs what I wrote.

Q2. For "How many orders were placed in January 2018?", what would a script, a workflow and an agent each do?
- Script: one SQL query I wrote, SELECT COUNT(*) FROM orders WHERE order_purchase_timestamp >= '2018-01-01' AND order_purchase_timestamp < '2018-02-01'. It returns 7,269 every time and makes no model call, so it has no model cost.
- Workflow: a model turns the English question into fixed fields like the month and the metric. My code puts those fields into a fixed SQL template and runs it. A model then writes one sentence with the result. The path never changes, and the model only does the language parts.
- Agent: the model asks for get_schema(), then asks for run_sql(), then writes the answer. That is 3 model calls for a question I already know how to answer. For a known question, a script is better.

Q3. Which three tasks in my project should stay scripts, and why?
- profile_db.py and check_gold.py. profile_db.py must give repeatable numbers (99,441 orders, 96,096 people). An agent could choose different queries on different runs. check_gold.py is my ruler for the agent, and a ruler that changes cannot measure anything.
- Loading the 9 CSVs into olist.db. It is the same every time and needs no understanding of language. I want the database rebuilt identically.
- The yearly revenue check for Q2 (46,586.33 + 6,922,900.24 + 8,452,975.20 = 15,422,461.77). The revenue definition must be fixed. If a model chose the definition, the proof would break.

Q4. When would an agent be the better choice? (Olist example)
"Which product categories grew fastest in the second half of 2017?" Nobody has written that query. The agent has to look at the schema, write a query, and maybe fix it. It also needs a definition of "grew fastest", which is a job for my metrics file at Level 4.
A second example is "Why did revenue drop in September 2018?" A careless agent would explain the drop with churn. An agent built to check the premise would run a monthly count with run_sql and find 16 orders in September against 6,512 in August (Lesson 7.4). A script would only print a small number. The agent learns this from the database through its tools, not from my notes or this log.

Q5. What are the four parts of an agent, and what will I build at Level 2?
- The model (the brain) decides what to do.
- The tools (the hands) are get_schema() and run_sql().
- The loop (the eyes) sends each observation back to the model, which decides again.
- The goal with a stopping rule is the question plus MAX_STEPS.
Three things that look similar are different. The history is the agent's working memory, kept and resent by my program. The trajectories/ folder is a record saved for me to study later. research_log.md is my own diary. The agent never reads schema_notes.md or this log.
At Level 2 I will build get_schema() reading the live database, run_sql() opening the database read-only with a row limit, the loop, MAX_STEPS, and trajectory logging.

Q6. What stays with the analyst, and what can an agent take over?
- An agent can take over writing and running SQL and counting, such as 7,269 orders in January 2018 or 18,551 people in the 90-day window.
- I keep deciding what "revenue" means. I found five totals. For Q2 I decided revenue = payment_value on delivered orders.
- I keep checking. An agent catches join inflation only if it is built with a check, such as comparing against a known total, which is how I found the 28%.
- I keep interpreting. The measurement showed that 162,591.95 of payments belongs to the 775 orders with no item rows. Reading what that means is my job.
- I keep questioning the premise, as with September 2018.

Q7. What am I still unsure about?
- How does the agent know it has the right answer and should stop? Learned: it does not know. The model stops when it decides it has an answer, and my program stops it at MAX_STEPS. Correctness is checked afterwards by comparing with gold answers (Level 5).
- How do I write "revenue = payment_value, delivered only" in a file the agent can read? A rough preview: a named definition with a description, the measure, the filter and the date column. I will design it properly at Level 4.
- How much revenue did the inner join in my first Q3 query lose? Still unmeasured.

Questions I can now answer:
- Who decides the next step? In a script, the person who wrote it. In a workflow, the person, with a model doing some steps. In an agent, the model.
- Why can't the model run a tool? It only produces text. My program runs the real function and sends back the result.
- Why does my program resend the whole history every time? The model remembers nothing between calls.
- Why does the program stop the loop and not the model? A confused model cannot be trusted to stop itself.
- If an agent gave me a number, what would I need to know to trust it? Which definition it used, which rows it included, whether the premise holds, and whether I can read the query it wrote.

Next: Level 1. Choose an API provider, put the key only in .env, and start Lesson 1.1.

## 2026-11-01 (Level 1, Lesson 1.1: first call to a model)

Purpose: make my first call to a language model from Python and see what goes out and what comes back.

Commands and purpose (written before running):
- `pip install google-genai`: install the library that sends requests to the Gemini API.
- `pip freeze > requirements.txt`: record exact versions so the setup can be rebuilt.
- `python src/hello_model.py`: send one prompt to the model and print the reply.

Happened:
- The first call worked. The model name comes from LLM_MODEL in .env (model used: ___).
- Prompt: "In one sentence, what is an e-commerce order?"
- Reply: "An e-commerce order is a customer's confirmed digital request to purchase specific goods or services from an online merchant, which initiates the payment, processing, and delivery workflow."
- Each call took about 1.5 to 2 minutes, which is much slower than I expected.

Learned:
- A request carries the model name, the prompt, settings and my API key. The response carries the reply text and a count of tokens used.
- The key and the model name live in .env and are read with load_dotenv(). The script holds only the names, never the secret.
- Every call stands alone. The model remembers nothing between calls.
- The model runs on the provider's servers, not on my MacBook.

Open question (not learned yet):
- Why is one call so slow? Candidates: the model spends time "thinking" before it answers, the free tier queues requests, the model name points to a heavy model, or the network is slow. A loop of 3 to 5 calls per question would be painfully slow at this speed, so I need the cause before Level 2.

Next: find the cause of the slow call, then Lesson 1.2 (tokens, the context window, temperature).

## 2026-11-01 (Level 1, Lesson 1.2: tokens and settings)

Purpose: see how text turns into tokens, and understand the settings that change what the model does.

Commands and purpose (written before running):
- `python src/count_tokens.py`: count the tokens in four texts (a sentence, an order_id, a SQL query, my schema notes) to see the difference between characters and tokens.

Happened:
- a short sentence: 44 characters, 14 tokens (3.1 characters per token)
- an order_id: 32 characters, 29 tokens (1.1)
- a SQL query: 119 characters, 44 tokens (2.7)
- my schema notes file: 10,977 characters, 4,037 tokens (2.7)

Learned:
- About one token per four characters, or about three-quarters of a word.
- An order_id use many tokens for its length, because It’s a random string with no word pieces, so it gets split into many tiny tokens. Plain English words are usually kept in bigger pieces.
- Everything in one call: my prompt, the history you resend, and the model’s reply, including any thinking tokens is the context window.

Next: System prompt and user prompt

## 2026-11-02 (Level 1, Lesson 1.3: system and user prompts)

Purpose: see how a system prompt changes what the model does with the same question.

Commands and purpose (written before running):
- `python src/prompt_demo.py`: send the same question twice, once without and once with a system prompt, and compare the two answers and their input tokens.

Prompt version: system prompt v1 (the text in src/prompt_demo.py).

Happened:
- First run failed with 503 UNAVAILABLE on gemini-flash-latest (model overloaded, not a mistake in my code).
- I listed the available names with src/list_models.py. gemini-2.5-flash-lite was in the list but failed for my key. I switched to gemini-3.5-flash (date: 2026-11-03).
- Without a system prompt: the model said it had no access to my data and asked for a file. Input tokens: 7.
- With system prompt v1: the answer followed the two-line format, said Needs clarification: yes, and noted that revenue has several definitions and that "last month" doesn't fit a dataset ending in October 2018. Input tokens: 113.
- The system prompt added 106 input tokens, repeated in every call.

Learned:
- Without a system prompt, the model knew nothing about Olist. It saw only “revenue for last month” and had no data to work with.
- Three parts of the system prompt shaped the second answer: the two-line format, the rule to answer yes when a metric has several definitions, and the context about the date range of the data.
- gemini-3.5-flash better for research than gemini-flash-latest, because it’s a fixed name, so it doesn’t silently move to another model. You still have to record the date, because providers retire names over time.