# Olist database: schema notes

Source: 9 CSV files from the Olist Brazilian E-Commerce dataset on Kaggle, loaded into SQLite (`data/olist.db`).
Every number below comes from `src/profile_db.py`, run on 2026-10-24. The script only reads the database.

This file is for people. The agent will get its schema from the live database (`get_schema()`), not from this file.

Items marked **not tested** are guesses or open questions. Everything else was measured.

---

## 1. The 9 tables at a glance

| Table | Rows | One row means | Key |
|---|---|---|---|
| orders | 99,441 | one order | `order_id` (tested: unique) |
| order_items | 112,650 | one item line inside an order | `order_id` + `order_item_id` together (tested: unique) |
| order_payments | 103,886 | one payment inside an order | `order_id` + `payment_sequential` (not tested) |
| order_reviews | 99,224 | one review record | none usable: `review_id` repeats |
| customers | 99,441 | one `customer_id` (a new one is made for every order) | `customer_id` (tested: unique) |
| products | 32,951 | one product | `product_id` (tested: unique) |
| sellers | 3,095 | one seller | `seller_id` (tested: unique) |
| product_category_name_translation | 71 | one Portuguese name and its English name | `product_category_name` (tested: unique) |
| geolocation | 1,000,163 | one coordinate sample for a zip prefix | none |

Pandas created these tables with no declared primary or foreign keys. SQLite does not stop duplicates or orphans, so every key above was tested with a query.

Time range of `order_purchase_timestamp`: 2016-09-04 to 2018-10-17. The data that is actually dense runs from 2017-01 to 2018-08 (see section 3).

---

## 2. How the tables connect

```
customers --1:1-- orders --1:many-- order_items --many:1-- products --many:1-- translation
                    |                    |
                    |                    +--many:1-- sellers
                    +--1:many-- order_payments
                    +--1:many-- order_reviews
```

What was tested (zero orphans means nothing points at a missing row):

- `orders.customer_id` to `customers`: 0 orders point to a missing customer. All 99,441 `customer_id` values in orders are different, so customers to orders is one to one.
- `order_items.order_id` to `orders`: 0 orphans.
- `order_items.product_id` to `products`: 0 orphans.
- `order_items.seller_id` to `sellers`: 0 orphans.
- `order_payments.order_id` to `orders`: 0 orphans.

Not tested: reviews to orders orphans, and the zip prefix links to geolocation.

The link from products to the translation table uses the Portuguese name text, not an id. Two product categories have no translation (section 3, products).

---

## 3. Table notes

### orders (99,441 rows)

Columns: `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`.

Status counts:

| Status | Orders |
|---|---|
| delivered | 96,478 |
| shipped | 1,107 |
| canceled | 625 |
| unavailable | 609 |
| invoiced | 314 |
| processing | 301 |
| created | 5 |
| approved | 2 |

Empty values (NULL):

- `order_approved_at`: 160
- `order_delivered_carrier_date`: 1,783
- `order_delivered_customer_date`: 2,965. Of these, 8 belong to orders marked `delivered`.
- `order_purchase_timestamp` and `order_estimated_delivery_date`: none.

Orders per purchase month:

| Month | Orders | Month | Orders |
|---|---|---|---|
| 2016-09 | 4 | 2017-11 | 7,544 |
| 2016-10 | 324 | 2017-12 | 5,673 |
| 2016-11 | no rows | 2018-01 | 7,269 |
| 2016-12 | 1 | 2018-02 | 6,728 |
| 2017-01 | 800 | 2018-03 | 7,211 |
| 2017-02 | 1,780 | 2018-04 | 6,939 |
| 2017-03 | 2,682 | 2018-05 | 6,873 |
| 2017-04 | 2,404 | 2018-06 | 6,167 |
| 2017-05 | 3,700 | 2018-07 | 6,292 |
| 2017-06 | 3,245 | 2018-08 | 6,512 |
| 2017-07 | 4,026 | 2018-09 | 16 |
| 2017-08 | 4,331 | 2018-10 | 4 |
| 2017-09 | 4,285 | | |
| 2017-10 | 4,631 | | |

Things to watch:

- 2016 is nearly empty, with no rows at all for 2016-11.
- Orders stop almost completely after 2018-08. A "drop" in 2018-09 is probably missing data, not a business event.
- Timestamps are text like `2018-07-24 20:41:37`. A filter like `<= '2018-08-31'` drops everything on Aug 31 after midnight. Use `>= '2018-08-01' AND < '2018-09-01'`.
- 775 orders have no rows in `order_items`. By status: unavailable 603, canceled 164, created 5, invoiced 2, shipped 1.
- 1 order has no payment row. It is a `delivered` order.

### order_items (112,650 rows)

- Covers 98,666 different orders (about 1.14 lines per order). The largest order has 21 lines.
- `order_item_id` counts the lines inside an order (1, 2, 3, ...). It is a line number, not a quantity.
- `price`: min 0.85, average 120.65, max 6,735.00, total 13,591,643.70.
- `freight_value`: min 0.00, average 19.99, max 409.68, total 2,251,909.54.
- `price + freight_value` total: 15,843,553.24.
- `shipping_limit_date` runs from 2016-09-19 to 2020-04-09. The 2020 date is long after the dataset ends.

### order_payments (103,886 rows)

- Covers 99,440 orders. 2,961 orders have more than one payment row. The most rows for one order is 29 (`payment_sequential` goes up to 29).
- Payment types:

| Type | Rows | Total value |
|---|---|---|
| credit_card | 76,795 | 12,542,084.19 |
| boleto | 19,784 | 2,869,361.27 |
| voucher | 5,775 | 379,436.87 |
| debit_card | 1,529 | 217,989.79 |
| not_defined | 3 | 0.00 |

- `payment_installments` runs from 0 to 24. 52,546 rows have exactly 1. A value of 0 looks odd (not tested how many rows).
- Total of all `payment_value`: 16,008,872.12.

### customers (99,441 rows)

- `customer_id` is different in every row, and orders uses each one exactly once. It identifies an order's buyer record, not a person.
- `customer_unique_id` identifies the person: 96,096 different people.
- 2,997 people have more than one `customer_id`, which means they placed more than one order. (99,441 minus 96,096 is 3,345, but that counts extra orders, not people.)
- 27 states. Top: SP 41,746, RJ 12,852, MG 11,635, RS 5,466, PR 5,045.

### products (32,951 rows)

- 73 different categories, and 610 products have no category (NULL).
- The same 610 products also have NULL name length, description length, and photo count.
- 2 products have NULL weight and size. Minimum weight is 0 (not tested how many).
- Column names have a spelling error: `product_name_lenght` and `product_description_lenght`. A query that spells them correctly will fail.
- 2 categories exist in products but not in the translation table:
  - `pc_gamer` (3 products)
  - `portateis_cozinha_e_preparadores_de_a...` (10 products; the name is cut off in the output)

### product_category_name_translation (71 rows)

- 71 Portuguese names and their English names, one each (for example `beleza_saude` is `health_beauty`).
- 71 is two fewer than the 73 categories in products.

### sellers (3,095 rows)

- 3,095 different sellers, in 23 states.
- Dirty data example: the smallest `seller_city` value is `04482255`, which is a number, not a city.

### order_reviews (99,224 rows)

- `review_id` is not unique: 98,410 different values in 99,224 rows.
- 98,673 different orders have a review, so about 768 orders have none. 547 orders have more than one review.
- Score counts: 1 star 11,424; 2 stars 3,151; 3 stars 8,179; 4 stars 19,142; 5 stars 57,328.
- `review_comment_title` is NULL in 87,656 rows. `review_comment_message` is NULL in 58,247 rows.
- `review_creation_date` ends 2018-08-31. `review_answer_timestamp` ends 2018-10-29.

### geolocation (1,000,163 rows)

- Only 19,015 different zip prefixes, so each prefix has many coordinate rows.
- Coordinates fall outside Brazil: latitude goes up to about 45 and longitude down to about -101. Brazil does not reach those values.
- City names are inconsistent (for example `* cidade` and `óleo` appear among the values).
- Not needed for levels L2 to L5.

---

## 4. Revenue: the numbers for each definition

"Revenue" is not stored in any column. There are several ways to build it, and they give different totals.

| Definition | Total |
|---|---|
| SUM of `order_items.price` (all orders that have items) | 13,591,643.70 |
| SUM of `price + freight_value` | 15,843,553.24 |
| SUM of `payment_value` (all payments) | 16,008,872.12 |
| SUM of `payment_value` for orders that have item rows | 15,846,280.17 |
| SUM of `payment_value` for `delivered` orders | 15,422,461.77 |

Where the gaps come from:

- 16,008,872.12 minus 15,846,280.17 is 162,591.95. That money was paid on orders that have no item rows (the 775 orders, mostly `unavailable` and `canceled`).
- 15,846,280.17 minus 15,843,553.24 is 2,726.93. This small gap between payments and `price + freight` is not explained yet (not tested).
- Vouchers are inside `payment_value` already, so they do not cause the gap.

Decisions you still have to make (write them in the research log):

1. Which orders count: all statuses, or only `delivered`?
2. Which measure: item price, item price plus freight, or payment value?
3. Which date: `order_purchase_timestamp` is the only date with no NULLs.

---

## 5. Join rules to remember

1. **Two "many" tables joined to one order multiply rows.** An order with 2 item lines and 2 payment rows becomes 4 rows. Sums then count money twice. Reduce one side to one row per order first, for example:

   ```sql
   SELECT order_id, SUM(payment_value) AS paid
   FROM order_payments
   GROUP BY order_id;
   ```

2. **Use a LEFT JOIN to the translation table.** An inner join silently drops the 610 products with no category and the 13 products in the 2 untranslated categories.
3. **Reviews can repeat per order.** 547 orders have more than one review. Reduce reviews to one row per order before joining.
4. **Count people with `customer_unique_id`**, not `customer_id`.
5. **Filter dates with a start and an end**, using `>= start AND < next day`.
6. **Always decide the `order_status` filter on purpose.** Do not leave it to chance.

---

## 6. Data quality list

- 2016 is nearly empty, and 2016-11 has no rows.
- 2018-09 has 16 orders and 2018-10 has 4.
- 775 orders have no item rows (mostly `unavailable` and `canceled`).
- 1 `delivered` order has no payment.
- 8 `delivered` orders have no delivery date.
- `payment_installments` has 0 values.
- `shipping_limit_date` has dates in 2020.
- `customer_id` is not a person.
- 610 products have no category, and 2 categories have no English name.
- Misspelled columns: `product_name_lenght`, `product_description_lenght`.
- `seller_city` contains a number (`04482255`).
- Geolocation has coordinates outside Brazil.
- `review_id` repeats.
- No declared keys anywhere, so nothing stops duplicates.

---

## 7. Still to test (not facts yet)

- Is (`order_id`, `payment_sequential`) unique in `order_payments`?
- How many payment rows have 0 installments?
- Do all `order_reviews.order_id` values exist in `orders`?
- How many products have weight 0?
