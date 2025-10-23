# etl.py
from __future__ import annotations
import os, time, math, requests, pandas as pd
from datetime import datetime

TODAY = datetime.now().strftime("%Y%m%d")
RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

# TODO: 여기에 본인 T-DATA OpenAPI 엔드포인트/키 입력
API_URL      = "https://t-data.seoul.go.kr/api/<데이터ID>/json"   # ← 실제 URL로 교체
SERVICE_KEY  = "YOUR_API_KEY"                                     # ← 본인 키

# 페이징/쿼리 파라미터 예시(데이터셋 가이드에 맞춰 조정)
# 일반적으로 date(yyyymmdd), page, size 같은 파라미터가 제공됨
BASE_PARAMS = {
    "serviceKey": SERVICE_KEY,
    "date": TODAY,       # yyyymmdd
    "page": 1,
    "size": 1000
}

def fetch_page(page:int) -> pd.DataFrame:
    params = {**BASE_PARAMS, "page": page}
    r = requests.get(API_URL, params=params, timeout=30)
    r.raise_for_status()
    js = r.json()
    # 응답 구조에 맞게 data/list 키를 조정하세요(T-DATA 문서 참조)
    items = js.get("data") or js.get("list") or []
    if not items:
        return pd.DataFrame()
    df = pd.json_normalize(items)

    # ---- 컬럼 표준화 (스키마에 맞춰 수정) ----
    # 예: date, hour, road_name, section, speed
    rename_map = {
        "일자":"date", "시간대":"hour", "도로명":"road_name",
        "구간명":"section", "링크ID":"link_id", "속도":"speed",
        "시간":"hour"  # '시간' 이름으로 오는 경우
    }
    for k,v in list(rename_map.items()):
        if k in df.columns and v not in df.columns:
            df = df.rename(columns={k:v})

    # hour 문자열 → 정수(0~23)로 정규화 시도
    if "hour" in df.columns:
        def norm_hour(x):
            s = str(x)
            # '07', '7', '07:00', '700' 등 다양한 형태 대응
            if ":" in s: s = s.split(":")[0]
            s = "".join([ch for ch in s if ch.isdigit()])
            if len(s) >= 2: s = s[-2:]  # 뒤 2자리 채택
            try: return int(s)
            except: return None
        df["hour"] = df["hour"].map(norm_hour)

    # date 표준화(yyyymmdd)
    if "date" in df.columns:
        df["date"] = df["date"].astype(str).str.replace("-", "", regex=False)

    # 필수 컬럼만 남기기(있는 것만 선택)
    keep = [c for c in ["date","hour","road_name","section","link_id","speed"] if c in df.columns]
    if keep:
        df = df[keep]

    return df

def main():
    # 1페이지 받아보고 총 건수/페이지 계산이 가능하면 처리(불가하면 그냥 1회만)
    try:
        df1 = fetch_page(1)
        if df1.empty:
            print("[WARN] page1 empty"); return
        dfs = [df1]
        # 추가 페이지를 더 받을 필요가 있으면 2..N 루프 (문서의 total/pageSize 참고)
        # 여기서는 보수적으로 2~5페이지만 더 시도
        for p in range(2, 6):
            time.sleep(0.2)
            dfn = fetch_page(p)
            if dfn.empty: break
            dfs.append(dfn)
        df = pd.concat(dfs, ignore_index=True).drop_duplicates()
        out = os.path.join(RAW_DIR, f"road_{TODAY}.csv")
        df.to_csv(out, index=False, encoding="utf-8")
        print(f"[OK] saved {len(df)} rows -> {out}")
    except requests.HTTPError as e:
        print("[HTTP ERROR]", e)
    except Exception as e:
        print("[ERROR]", e)

if __name__ == "__main__":
    main()
