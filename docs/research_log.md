## 2026-10-24 (Week 0: setup)

Tried: created the repo, downloaded Olist from Kaggle (9 CSVs), wrote a script that loads them into olist.db (SQLite), then profiled every table with src/profile_db.py and wrote docs/schema_notes.md.

Happened:
- Loaded 9 tables: orders 99,441 rows, order_items 112,650, order_payments 103,886, customers 99,441, products 32,951, sellers 3,095, plus reviews, geolocation and the category translation table.
- First query failed: SELECT * FROM orders_payments. The real name is order_payments.
- order_payments: 103,886 rows for 99,440 orders; 2,961 orders have more than one payment row.
- Revenue totals: price 13,591,643.70 | price + freight 15,843,553.24 | payment_value 16,008,872.12.
- customers: 99,441 rows, 96,096 people; 2,997 people have more than one customer_id.
- Data is dense from 2017-01 to 2018-08. 2018-09 has 16 orders, 2018-10 has 4.
- 162,591.95 of the payment total belongs to 775 orders that have no item rows.

Learned:
- Revenue is not one number. The definition changes the answer, which is the reason for the semantic layer (L4).
- Joining payments to items can repeat rows and inflate sums.
- "Customer" also needs a definition (customer_id or customer_unique_id).
- pandas created the tables without primary or foreign keys, so I must check relationships by hand.
- I guessed vouchers caused the payment gap. The data says orders without items did.

Ideas to test later (not learned yet):
- get_schema() may work better with row counts and a few sample values. Compare with and without in L2/L3.

Eval notes: wrote 5 draft dev questions in evals/dev_questions.csv. None has been run, since no agent exists. Their difficulty is expected, not observed.

Details: docs/schema_notes.md

Next: L0 note, my own definition of agent vs script vs chatbot, with 3 examples where an agent is worse than a script.