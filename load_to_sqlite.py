import os, glob, sqlite3, pandas as pd
os.makedirs("data", exist_ok=True)
DB = "data/app.db"

def append(csv_glob, table, keys):
    files = sorted(glob.glob(csv_glob))
    if not files:
        print("[SKIP] no files", csv_glob); return
    with sqlite3.connect(DB) as conn:
        for f in files:
            df = pd.read_csv(f)
            df.to_sql(table, conn, if_exists="append", index=False)
        # 간단 dedup (keys 기준)
        cols = ",".join(keys)
        conn.execute(f"""
          DELETE FROM {table}
          WHERE rowid NOT IN (
            SELECT MIN(rowid) FROM {table} GROUP BY {cols}
          );
        """)
        conn.commit()
    print(f"[OK] loaded -> {table} (dedup by {keys})")

# 도로: 하루(date)+구간(section or link_id)+시간(hour)
append("data/raw/road_*.csv", "logs_road", ["date","section","hour"])
