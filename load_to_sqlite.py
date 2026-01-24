# -*- coding: utf-8 -*-
"""
CSV(또는 유사 스키마)를 읽어 표준 스키마 logs_road(date,hour,speed)로
EDA 레포의 data/app.db 에 업서트(중복이면 업데이트)합니다.
"""
import os, glob, sqlite3
import pandas as pd

# ▶▶ DB 경로: 환경변수(APP_DB_PATH) 우선, 없으면 로컬 기본값
DB = os.getenv('APP_DB_PATH', os.path.join('.', 'data', 'app.db'))
os.makedirs(os.path.dirname(DB), exist_ok=True)

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """다양한 입력 컬럼을 표준 컬럼(date,hour,speed)로 통일"""
    df = df.copy()

    # 1) 가장 흔한 패턴: timestamp / value
    if {"timestamp", "value"}.issubset(df.columns):
        ts = pd.to_datetime(df["timestamp"], errors="coerce")
        out = pd.DataFrame({
            "date": ts.dt.strftime("%Y%m%d"),
            "hour": ts.dt.hour,
            "speed": pd.to_numeric(df["value"], errors="coerce")
        })
        return out.dropna(subset=["date", "hour", "speed"])

    # 2) 이미 표준 스키마
    if {"date", "hour", "speed"}.issubset(df.columns):
        out = df[["date", "hour", "speed"]].copy()
        out["date"]  = out["date"].astype(str).str.replace("-", "", regex=False)
        out["hour"]  = pd.to_numeric(out["hour"], errors="coerce")
        out["speed"] = pd.to_numeric(out["speed"], errors="coerce")
        return out.dropna(subset=["date", "hour", "speed"])

    # 3) 한국어/혼합 컬럼 가벼운 대응
    m = df.rename(columns={
        "일자": "date", "시간": "hour", "시간대": "hour",
        "속도": "speed", "value": "speed"
    })
    if "timestamp" in m.columns and "date" not in m.columns:
        ts = pd.to_datetime(m["timestamp"], errors="coerce")
        m["date"] = ts.dt.strftime("%Y%m%d")
        m["hour"] = ts.dt.hour
    if {"date", "hour", "speed"}.issubset(m.columns):
        m["date"]  = m["date"].astype(str).str.replace("-", "", regex=False)
        m["hour"]  = pd.to_numeric(m["hour"], errors="coerce")
        m["speed"] = pd.to_numeric(m["speed"], errors="coerce")
        return m.dropna(subset=["date", "hour", "speed"])[["date", "hour", "speed"]]

    return pd.DataFrame(columns=["date", "hour", "speed"])

def upsert(conn: sqlite3.Connection, rows):
    """(date,hour) 유니크 키로 업서트"""
    conn.execute("CREATE TABLE IF NOT EXISTS logs_road(date TEXT, hour INTEGER, speed REAL)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_logs_road_date_hour ON logs_road(date, hour)")
    conn.executemany(
        """
        INSERT INTO logs_road(date,hour,speed)
        VALUES (?,?,?)
        ON CONFLICT(date,hour) DO UPDATE SET speed=excluded.speed
        """,
        rows,
    )

def read_csv_flex(path: str) -> pd.DataFrame:
    """CSV를 인코딩 자동 재시도하며 읽기"""
    for enc in ["utf-8-sig", "utf-8", "cp949", "euc-kr"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    # 최후: 무시하고 읽기
    return pd.read_csv(path, encoding="cp949", errors="ignore")

def main():
    files = sorted(glob.glob("data/*.csv") + glob.glob("data/raw/*.csv"))
    if not files:
        print("[INFO] no input csv"); return

    total_new = 0
    with sqlite3.connect(DB) as con:
        for fp in files:
            try:
                df = read_csv_flex(fp)
            except Exception as e:
                print(f"[ERR] read {fp}: {e}")
                continue

            out = normalize(df)
            if out.empty:
                print(f"[SKIP] {fp} (no usable columns)")
                continue

            rows = list(map(tuple, out[["date", "hour", "speed"]].itertuples(index=False, name=None)))

            before = con.execute("SELECT COUNT(*) FROM logs_road").fetchone()[0]
            upsert(con, rows)
            after  = con.execute("SELECT COUNT(*) FROM logs_road").fetchone()[0]
            inc = max(0, after - before)
            total_new += inc

            print(f"[OK] {os.path.basename(fp)} -> upsert {len(rows)} rows (unique +{inc})")

        con.commit()

    print(f"[DONE] unique rows increased: +{total_new}")
    # 상태 요약
    with sqlite3.connect(DB) as con:
        cnt, = con.execute("SELECT COUNT(*) FROM logs_road").fetchone()
        mind, maxd = con.execute("SELECT MIN(date), MAX(date) FROM logs_road").fetchone()
        print(f"[STATS] COUNT={cnt}, DATE_RANGE=({mind} ~ {maxd})")

if __name__ == "__main__":
    main()
