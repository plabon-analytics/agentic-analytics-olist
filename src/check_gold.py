import csv
import sqlite3

# Open the database read-only: this script only looks, it never changes data.
conn = sqlite3.connect("file:data/olist.db?mode=ro", uri=True)

with open("evals/dev_questions.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["gold_sql"] == "NONE":
            print(f"Q{row['id']}: no SQL (analytical question)")
            continue
        result = conn.execute(row["gold_sql"]).fetchall()
        print(f"Q{row['id']}: result {result} | recorded {row['checked_result']}")

conn.close()
