# 서울 출퇴근 도로속도 ETL (SQLite)

[![Python](https://img.shields.io/badge/Python-3.x-informational?logo=python)]()
[![Pandas](https://img.shields.io/badge/Pandas-ETL-blue?logo=pandas)]()
[![SQLite](https://img.shields.io/badge/SQLite-db-blue?logo=sqlite)]()
[![Last Commit](https://img.shields.io/github/last-commit/cxo-ca/project-etl-sql)]()
![Issues](https://img.shields.io/github/issues/cxo-ca/project-etl-sql)
![Stars](https://img.shields.io/github/stars/cxo-ca/project-etl-sql)
[![License](https://img.shields.io/badge/license-MIT-green)]()

수집(Extract) → 정제/표준화(Transform) → SQLite 적재(Load).  
결과는 **EDA 레포의 `data/app.db`** 에 누적되어 대시보드에서 사용됩니다. :contentReference[oaicite:6]{index=6}

---

## Quickstart (3분 내 실행) :contentReference[oaicite:7]{index=7}

### 1) 설치
```bash
pip install -r requirements.txt
```

### 2) 실행 (샘플 데이터 생성 → DB 적재)
```
# 1) 샘플 생성(AM 08시/PM 18시, 30~60 km/h)
py etl.py

# 2) 표준 스키마로 적재(logs_road 누적 + 중복 제거)
py load_to_sqlite.py
```

### 3) 결과 확인(로컬)
- 지정한 DB 파일(app.db)이 생성/갱신됩니다.
- DB 내 logs_road 테이블에 데이터가 누적됩니다

## Results (무엇이 만들어지나)
### Output
- SQLite DB: app.db
- Table: logs_road(date TEXT, hour INTEGER, speed REAL)

### Expected behavior
- 실행할 때마다 logs_road에 누적 적재됩니다.
- (date, hour) 유니크 키 기준으로 중복은 업데이트됩니다(업서트).

### Quick sanity check (optional)
```
-- SQLite에서 확인
SELECT COUNT(*) AS n_rows FROM logs_road;

-- 최근 적재 데이터 일부 확인
SELECT date, hour, speed
FROM logs_road
ORDER BY date DESC, hour DESC
LIMIT 10;
```

## 환경변수: APP_DB_PATH (중요)
ETL이 적재할 SQLite DB 경로는 APP_DB_PATH로 제어하는 것을 권장합니다.

### 로컬에서 같이 쓸 때(기본: EDA 레포 내부 DB를 바라보기)
레포 루트에 .env를 만들고(커밋 금지):
```
APP_DB_PATH=../project-eda-dashboard/data/app.db
```
### ETL 레포 내부에 DB를 둘 때(단독 실행)
```
APP_DB_PATH=./data/app.db
```

(중요) 상대경로는 ‘현재 실행하는 레포(ETL)’ 기준 입니다.
즉, ETL 레포에서 APP_DB_PATH=../project-eda-dashboard/data/app.db라면 “ETL 폴더 기준으로 한 단계 위로 가서 EDA 폴더의 DB를 가리킨다”는 뜻입니다.

## 표준 스키마
```
logs_road(
  date  TEXT    -- 'YYYYMMDD'
  hour  INTEGER -- 0~23
  speed REAL    -- km/h
)
```

## 자동화(선택, 작업 스케줄러)
- 스크립트: run_etl.ps1

### 등록 예시
```
schtasks /Create /SC DAILY /ST 06:50 /TN 'Road ETL daily' ^
  /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""%USERPROFILE%\Desktop\project-etl-sql\run_etl.ps1""" ^
  /RL LIMITED
```

## 트러블슈팅
- EDA에서 no such table: logs_road
  - 대시보드가 다른 DB 파일을 열고 있는 상태입니다. APP_DB_PATH(ETL)와 대시보드의 DB 경로가 같은 파일을 가리키게 통일하세요.
- unable to open database file
  - DB 경로/부모 폴더 존재 여부를 확인하세요.

## 라이선스 / 주의사항
교육/데모 목적. 실제 운영 전에는 데이터 출처 약관을 확인하세요.
