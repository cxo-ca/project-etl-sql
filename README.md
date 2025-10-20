일 1회 자동 수집 → SQLite 적재, 주간 리포트 5분 내 생성
https://sites.google.com/view/cxo-ca
etl, sql, python, sqlite, automation

ETL: Daily ETL → load to SQLite, weekly report in 5 min

## 실행 방법
```bash
pip install -r requirements.txt
python etl.py

## 결과
- etl.py 실행 시 data/ 폴더에 CSV 자동 생성
- load_to_sqlite.py로 CSV를 SQLite DB(data/app.db)의 logs 테이블에 적재 확인
