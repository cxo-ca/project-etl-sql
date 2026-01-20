# 서울 출퇴근 도로속도 ETL (SQLite)

[![Python](https://img.shields.io/badge/Python-3.x-informational?logo=python)]()
[![Pandas](https://img.shields.io/badge/Pandas-ETL-blue?logo=pandas)]()
[![SQLite](https://img.shields.io/badge/SQLite-db-blue?logo=sqlite)]()
[![Last Commit](https://img.shields.io/github/last-commit/cxo-ca/project-etl-sql)]()
![Issues](https://img.shields.io/github/issues/cxo-ca/project-etl-sql)
![Stars](https://img.shields.io/github/stars/cxo-ca/project-etl-sql)
[![License](https://img.shields.io/badge/license-MIT-green)]()

수집(Extract) → 정제/표준화(Transform) → SQLite 적재(Load).  
결과는 **EDA 레포의 `data/app.db`** 에 누적되어 대시보드에서 사용됩니다.

---

## Quickstart (3분 내 실행)

### 1) 설치
```bash
pip install -r requirements.txt

### 2) 실행 (샘플 데이터 생성 → DB 적재)
# 1) 샘플 생성(AM 08시/PM 18시, 30~60 km/h)
py etl.py

# 2) 표준 스키마로 적재(logs_road 누적 + 중복 제거)
py load_to_sqlite.py

3) 결과 확인(로컬)
- load_to_sqlite.py에서 지정한 경로에 app.db가 생성/갱신됩니다.
- DB 내 logs_road 테이블에 데이터가 누적됩니다.

Results (무엇이 만들어지나)
Output
- SQLite DB: app.db
- Table: logs_road(date TEXT, hour INTEGER, speed REAL)

Expected behavior
- 실행할 때마다 logs_road에 누적 적재됩니다.
- 중복 행이 있으면 제거됩니다.
- EDA 대시보드는 동일한 DB(data/app.db)를 열어 시각화에 사용합니다.

Quick sanity check (optional)
-- SQLite에서 확인
SELECT COUNT(*) AS n_rows FROM logs_road;

-- 최근 적재 데이터 일부 확인
SELECT date, hour, speed
FROM logs_road
ORDER BY date DESC, hour DESC
LIMIT 10;

출력 DB (단일 경로로 통일)
- Windows 예: C:\Users\USER\Desktop\project-eda-dashboard\data\app.db
- load_to_sqlite.py 상단 경로 예시:

import os

HOME = os.path.expanduser("~")
DB = os.path.join(HOME, "Desktop", "project-eda-dashboard", "data", "app.db")
os.makedirs(os.path.dirname(DB), exist_ok=True)

팁: EDA 레포와 ETL 레포가 서로 다른 DB 파일을 가리키면, 대시보드에서 no such table: logs_road가 발생합니다.
반드시 EDA의 data/app.db로 통일하세요.

폴더 구조
project-etl-sql/  
 ├─ etl.py               # 샘플/원천 데이터 수집 (CSV 생성)  
 ├─ load_to_sqlite.py    # CSV → 표준 스키마 변환 후 logs_road 적재  
 ├─ data/  
 │   ├─ raw/             # 원본 CSV 저장(옵션)  
 │   └─ sample_*.csv     # 예시 생성물  
 └─ logs/                # 스케줄 실행 로그(옵션)

표준 스키마
logs_road(
  date  TEXT    -- 'YYYYMMDD'
  hour  INTEGER -- 0~23
  speed REAL    -- km/h
)

자동화(선택, 작업 스케줄러)
- 스크립트: run_etl.ps1

등록 예시
schtasks /Create /SC DAILY /ST 06:50 /TN "Road ETL daily" ^
  /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""%USERPROFILE%\Desktop\project-etl-sql\run_etl.ps1""" ^
  /RL LIMITED

작업 스케줄러 → 동작 인수 예시
-ExecutionPolicy Bypass -File "C:\Users\USER\Desktop\project-etl-sql\run_etl.ps1"

트러블슈팅
- EDA에서 no such table: logs_road
  - EDA가 다른 DB를 여는 중입니다. EDA의 data/app.db로 통일하세요.
- unable to open database file
  - DB 경로/부모 폴더를 확인하세요. project-eda-dashboard\data\app.db 경로가 실제로 존재해야 합니다.

마지막 빠른 점검(선택)
# 대시보드 실행 → 화면에서 Using DB 경로 확인
cd $EDA
py -m streamlit run app/app.py

라이선스 / 주의사항
교육/데모 목적. 실제 운영 전에는 데이터 출처(T-DATA/TOPIS) 약관 확인.
