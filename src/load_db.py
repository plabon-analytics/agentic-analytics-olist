import sqlite3
from pathlib import Path
import pandas as pd

conn = sqlite3.connect("data/olist.db")
for f in Path("data").glob("*.csv"):
    name = f.stem.replace("olist_", "").replace("_dataset", "")
    pd.read_csv(f).to_sql(name, conn, if_exists="replace", index=False)
    print("loaded", name)
conn.close()
