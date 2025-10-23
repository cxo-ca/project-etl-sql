# 서울 출퇴근 도로속도 ETL (SQLite)

수집(Extract) → 정제/표준화(Transform) → SQLite 적재(Load).  
결과는 **EDA 레포의 `data/app.db`** 에 누적되어 대시보드에서 사용됩니다.

## 출력 DB (단일 경로로 통일)
- Windows 예: `C:\Users\USER\Desktop\project-eda-dashboard\data\app.db`
- `load_to_sqlite.py` 상단 경로 예시:
```python
import os
HOME = os.path.expanduser("~")
DB = os.path.join(HOME, "Desktop", "project-eda-dashboard", "data", "app.db")
os.makedirs(os.path.dirname(DB), exist_ok=True)

빠른 실행
# 1) 샘플 생성(AM 08시/PM 18시, 30~60 km/h)
py etl.py
# 2) 표준 스키마로 적재(logs_road 누적 + 중복 제거)
py load_to_sqlite.py

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
매일 06:50 실행 예:
# run_etl.ps1
$ErrorActionPreference = 'Stop'
Set-Location $env:USERPROFILE\Desktop\project-etl-sql
py etl.py
py load_to_sqlite.py


작업 스케줄러 → 동작 인수:
-ExecutionPolicy Bypass -File "C:\Users\USER\Desktop\project-etl-sql\run_etl.ps1"

트러블슈팅
EDA에서 no such table: logs_road
→ EDA가 다른 DB를 여는 중. EDA의 data/app.db로 경로 통일.
unable to open database file
→ 경로/부모 폴더 없음. project-eda-dashboard\data\app.db 존재 확인.
AM/PM 카드가 비어 있음
→ 최근 n일에 07–09/17–19 데이터가 없을 수 있음. 샘플 재생성 후 적재.

라이선스
교육/데모 목적. 실제 운영 전에는 데이터 출처(T-DATA/TOPIS) 약관 확인.
::contentReference[oaicite:0]{index=0}
