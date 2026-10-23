# Research Log

## 2026-10-24 (Week 0: setup)

Tried: created the repo, downloaded Olist from Kaggle (9 CSVs), wrote a script that loads them into olist.db (SQLite).

Happened:
- Loaded 9 tables: orders 99,441 rows, order_items 112,650, order_payments 103,886, customers 99,441, products 32,951, sellers 3,095, plus reviews, geolocation and the category translation table.
- First query failed: SELECT * FROM orders_payments. The real name is order_payments.
- order_payments has more than one row per order (103,886 rows, 99,440 distinct orders). Means installments - if you join it blindly, you inflate revenue.
- Revenue can be SUM(price) = 13,591,643.7, price + freight = 15,843,553.24, or SUM(payment_value) = 16,008,872.12. Difference between price+freight and payments = 165,318.88.
- customers has as many rows as orders because customer_id is new for every order. Distinct customer_unique_id = 96,096.
- Orders per month: data is dense from 2016-09 to 2018-08 (peak 7,544 in 2017-11), and thin after: 2018-09 = 16, 2018-10 = 4. So "Why did revenue drop in Sept 2018?" is a TRICK QUESTION - data ends.

Learned:
- Revenue is not one number. The definition changes the answer by 2.4M (13.5M vs 16M), which is the reason for the semantic layer (L4).
- Joining payments to items can repeat rows and inflate sums by ~3.4k rows.
- "Customer" also needs a definition (customer_id = order instance vs customer_unique_id = real person).
- pandas created the tables without primary or foreign keys, so I must check relationships by hand.

Ideas to test later (not learned yet):
- get_schema() may work better with row counts and a few sample values. Compare with and without in L2/L3.

Eval notes: wrote 5 draft dev questions in evals/dev_questions.csv. None has been run, since no agent exists. Their difficulty is expected, not observed.

Next: L0 note, my own definition of agent vs script vs chatbot, with 3 examples where an agent is worse than a script.
