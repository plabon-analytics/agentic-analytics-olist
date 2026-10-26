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

Happened:
- Q2 check: 2016 = 46,586.33, 2017 = 6,922,900.24, 2018 = 8,452,975.20. Together 15,422,461.77, which equals the delivered payment total in the schema notes. Q2 is proven.
- Delivered item price total: 13,221,498.11.
- Q4 window: 18,780 orders, 18,468 of them delivered, 18,551 people (any status). Delivered-only people were 18,248.

Learned:
- A gold query must do what the written decision says. My first Q3 used an inner join to the translation table, which silently drops products with no category or no translation. A LEFT JOIN with COALESCE keeps them.
- The question text and the SQL must say the same thing. My first Q4 question said "placed an order" but the SQL kept only delivered orders. The agent sees the question and never sees my notes.
- A -- comment inside a CSV cell can swallow the rest of the query. Results and decisions go in the notes column.
- The word "revenue" in Q2 is undefined on purpose. The metric file at L4 will supply the definition, and the gap between L3 and L4 answers is the experiment.

Ideas to test later (not learned yet):
- How much revenue the inner join in my first Q3 query lost.
- Whether the second-place category is close enough to health_beauty that a different revenue definition flips the winner.

Eval notes: dev_questions.csv has 5 questions with gold SQL for Q1 to Q4 and a rubric for Q5. Q1 and Q3 results still need a re-run to confirm. None of the questions has been run on an agent, since no agent exists.

Next: run src/check_gold.py to confirm the saved SQL gives the recorded results, then start the Level 0 lesson.
