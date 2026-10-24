import sqlite3
from pathlib import Path
import pandas as pd

conn = sqlite3.connect("file:data/olist.db?mode=ro", uri=True)
out = []


def show(title, sql):
    df = pd.read_sql_query(sql, conn)
    out.append(f"\n=== {title} ===")
    out.append(df.to_string(index=False, max_colwidth=40) if len(df) else "(no rows)")


tables = [r[0] for r in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]

# Part 1: every column of every table, plus 3 sample rows
for t in tables:
    info = conn.execute(f'PRAGMA table_info("{t}")').fetchall()
    parts = []
    for cid, col, ctype, *rest in info:
        parts.append(
            f"SELECT '{col}' AS col, '{ctype}' AS type, COUNT(*) AS total, "
            f'COUNT("{col}") AS non_null, COUNT(DISTINCT "{col}") AS distinct_vals, '
            f'SUBSTR(CAST(MIN("{col}") AS TEXT),1,30) AS min_val, '
            f'SUBSTR(CAST(MAX("{col}") AS TEXT),1,30) AS max_val FROM "{t}"'
        )
    show(f"TABLE {t}: columns", " UNION ALL ".join(parts))
    show(f"TABLE {t}: 3 sample rows", f'SELECT * FROM "{t}" LIMIT 3')

# Part 2: specific checks
checks = [
    ("orders: rows, distinct order_id, distinct customer_id",
     "SELECT COUNT(*) AS n_rows, COUNT(DISTINCT order_id) AS order_ids, COUNT(DISTINCT customer_id) AS customer_ids FROM orders"),
    ("orders: count by status",
     "SELECT order_status, COUNT(*) AS n FROM orders GROUP BY order_status ORDER BY n DESC"),
    ("orders: count by purchase month",
     "SELECT strftime('%Y-%m', order_purchase_timestamp) AS month, COUNT(*) AS orders FROM orders GROUP BY month ORDER BY month"),
    ("orders: delivered orders with no delivered-customer date",
     "SELECT COUNT(*) AS n FROM orders WHERE order_status = 'delivered' AND order_delivered_customer_date IS NULL"),
    ("orders: orders with no item rows, by status",
     "SELECT order_status, COUNT(*) AS n FROM orders WHERE order_id NOT IN (SELECT order_id FROM order_items) GROUP BY order_status ORDER BY n DESC"),
    ("orders: orders with no payment rows, by status",
     "SELECT order_status, COUNT(*) AS n FROM orders WHERE order_id NOT IN (SELECT order_id FROM order_payments) GROUP BY order_status ORDER BY n DESC"),
    ("order_items: rows, distinct orders, distinct lines, max item number",
     "SELECT COUNT(*) AS n_rows, COUNT(DISTINCT order_id) AS orders, COUNT(DISTINCT order_id || '-' || order_item_id) AS distinct_lines, MAX(order_item_id) AS max_item_id FROM order_items"),
    ("order_items: price and freight summary",
     "SELECT MIN(price) AS min_price, AVG(price) AS avg_price, MAX(price) AS max_price, SUM(price) AS sum_price, MIN(freight_value) AS min_freight, AVG(freight_value) AS avg_freight, MAX(freight_value) AS max_freight, SUM(freight_value) AS sum_freight, SUM(price + freight_value) AS sum_price_plus_freight FROM order_items"),
    ("order_items: orphans",
     "SELECT (SELECT COUNT(*) FROM order_items WHERE order_id NOT IN (SELECT order_id FROM orders)) AS no_order, (SELECT COUNT(*) FROM order_items WHERE product_id NOT IN (SELECT product_id FROM products)) AS no_product, (SELECT COUNT(*) FROM order_items WHERE seller_id NOT IN (SELECT seller_id FROM sellers)) AS no_seller"),
    ("order_payments: rows, distinct orders, max sequential, orders with more than one payment",
     "SELECT COUNT(*) AS n_rows, COUNT(DISTINCT order_id) AS orders, MAX(payment_sequential) AS max_sequential, (SELECT COUNT(*) FROM (SELECT order_id FROM order_payments GROUP BY order_id HAVING COUNT(*) > 1)) AS orders_with_multi_payments FROM order_payments"),
    ("order_payments: by payment type",
     "SELECT payment_type, COUNT(*) AS n, SUM(payment_value) AS total FROM order_payments GROUP BY payment_type ORDER BY n DESC"),
    ("order_payments: installments",
     "SELECT MIN(payment_installments) AS min_inst, MAX(payment_installments) AS max_inst, SUM(payment_installments = 1) AS rows_with_1_inst FROM order_payments"),
    ("order_payments: totals (all, orders with items, delivered orders)",
     "SELECT (SELECT SUM(payment_value) FROM order_payments) AS all_payments, (SELECT SUM(payment_value) FROM order_payments WHERE order_id IN (SELECT order_id FROM order_items)) AS for_orders_with_items, (SELECT SUM(payment_value) FROM order_payments WHERE order_id IN (SELECT order_id FROM orders WHERE order_status = 'delivered')) AS for_delivered_orders"),
    ("order_payments: payments without an order",
     "SELECT COUNT(*) AS n FROM order_payments WHERE order_id NOT IN (SELECT order_id FROM orders)"),
    ("customers: rows, distinct customer_id, distinct people, people with several customer_ids",
     "SELECT COUNT(*) AS n_rows, COUNT(DISTINCT customer_id) AS customer_ids, COUNT(DISTINCT customer_unique_id) AS people, (SELECT COUNT(*) FROM (SELECT customer_unique_id FROM customers GROUP BY customer_unique_id HAVING COUNT(*) > 1)) AS people_with_multiple_ids FROM customers"),
    ("customers: orders pointing to a missing customer",
     "SELECT COUNT(*) AS n FROM orders WHERE customer_id NOT IN (SELECT customer_id FROM customers)"),
    ("customers: top 10 states",
     "SELECT customer_state, COUNT(*) AS n FROM customers GROUP BY customer_state ORDER BY n DESC LIMIT 10"),
    ("products: rows, distinct ids, categories, NULL category",
     "SELECT COUNT(*) AS n_rows, COUNT(DISTINCT product_id) AS product_ids, COUNT(DISTINCT product_category_name) AS categories, SUM(product_category_name IS NULL) AS null_category FROM products"),
    ("products: categories missing from the translation table",
     "SELECT p.product_category_name, COUNT(*) AS products FROM products p LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name WHERE t.product_category_name IS NULL AND p.product_category_name IS NOT NULL GROUP BY p.product_category_name"),
    ("translation: rows and distinct Portuguese names",
     "SELECT COUNT(*) AS n_rows, COUNT(DISTINCT product_category_name) AS distinct_pt FROM product_category_name_translation"),
    ("sellers: rows and distinct ids",
     "SELECT COUNT(*) AS n_rows, COUNT(DISTINCT seller_id) AS seller_ids FROM sellers"),
    ("order_reviews: rows, distinct review_id, distinct orders, orders with several reviews",
     "SELECT COUNT(*) AS n_rows, COUNT(DISTINCT review_id) AS review_ids, COUNT(DISTINCT order_id) AS orders, (SELECT COUNT(*) FROM (SELECT order_id FROM order_reviews GROUP BY order_id HAVING COUNT(*) > 1)) AS orders_with_multi_reviews FROM order_reviews"),
    ("order_reviews: score counts",
     "SELECT review_score, COUNT(*) AS n FROM order_reviews GROUP BY review_score ORDER BY review_score"),
    ("geolocation: rows and distinct zip prefixes",
     "SELECT COUNT(*) AS n_rows, COUNT(DISTINCT geolocation_zip_code_prefix) AS zip_prefixes FROM geolocation"),
]
for title, sql in checks:
    show(title, sql)

Path("data/db_profile.txt").write_text("\n".join(out), encoding="utf-8")
print("Done. Wrote data/db_profile.txt")