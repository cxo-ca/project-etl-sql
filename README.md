# 서울 출퇴근 도로속도 ETL

> 서울 출퇴근 도로속도 데이터를 수집·정제·표준화한 뒤 SQLite에 적재하는 ETL 프로젝트입니다.

![Python](https://img.shields.io/badge/Python-3.x-informational?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-ETL-blue?logo=pandas)
![SQLite](https://img.shields.io/badge/SQLite-database-blue?logo=sqlite)
![Last Commit](https://img.shields.io/github/last-commit/cxo-ca/project-etl-sql)
![Issues](https://img.shields.io/github/issues/cxo-ca/project-etl-sql)
![Stars](https://img.shields.io/github/stars/cxo-ca/project-etl-sql)

---

## 프로젝트 개요

이 프로젝트는 출퇴근 시간대 교통 데이터를 분석하기 위한 데이터 파이프라인입니다.

수집한 도로속도 데이터를 표준 스키마로 변환한 뒤 SQLite 데이터베이스의 `logs_road` 테이블에 누적 적재합니다.

적재된 데이터는 별도 EDA 대시보드 프로젝트에서 AM/PM 평균속도 KPI와 시각화 지표로 활용됩니다.

---

## 프로젝트 목적

단순히 SQL 파일을 만드는 것이 아니라, 분석 대시보드가 바로 사용할 수 있는 형태로 데이터를 정리하는 것을 목표로 했습니다.

이 프로젝트에서 해결하려는 문제는 다음과 같습니다.

- 교통 데이터의 날짜, 시간, 속도 값을 일관된 스키마로 관리하기
- 매일 실행해도 중복 데이터가 쌓이지 않도록 처리하기
- SQLite DB를 통해 대시보드 프로젝트와 연결 가능한 구조 만들기
- 로컬 환경에서도 쉽게 실행 가능한 ETL 흐름 구성하기

---

## ETL 흐름

~~~text
Extract
  ↓
Transform
  ↓
Load
  ↓
SQLite logs_road
  ↓
Streamlit EDA Dashboard
~~~

| 단계 | 설명 |
|---|---|
| Extract | 원천 데이터를 불러오거나 샘플 데이터를 생성 |
| Transform | 날짜, 시간, 평균속도 컬럼을 표준 형식으로 정리 |
| Load | SQLite DB의 `logs_road` 테이블에 적재 |
| Upsert | `(date, hour)` 기준으로 중복 데이터를 업데이트 |

---

## 표준 스키마

~~~sql
logs_road (
    date  TEXT,     -- YYYYMMDD
    hour  INTEGER,  -- 0~23
    speed REAL      -- km/h
);
~~~

| 컬럼 | 타입 | 설명 |
|---|---|---|
| date | TEXT | 날짜, `YYYYMMDD` 형식 |
| hour | INTEGER | 시간, 0~23 |
| speed | REAL | 평균속도, km/h |

---

## 핵심 기능

| 기능 | 설명 |
|---|---|
| 샘플 데이터 생성 | AM 08시, PM 18시 기준 도로속도 데이터 생성 |
| SQLite 적재 | 정제된 데이터를 `app.db`에 저장 |
| 중복 방지 | `(date, hour)` 기준으로 기존 데이터 업데이트 |
| 환경변수 지원 | `APP_DB_PATH`로 DB 저장 위치 제어 |
| 대시보드 연동 | EDA 프로젝트의 `data/app.db`와 연결 가능 |
| 자동화 준비 | PowerShell 스크립트와 작업 스케줄러 등록 가능 |

---

## 기술 스택

| 구분 | 사용 기술 |
|---|---|
| Language | Python |
| Data Processing | Pandas |
| Database | SQLite |
| Config | python-dotenv |
| Automation | PowerShell, Windows Task Scheduler |

---

## 폴더 구조

~~~text
project-etl-sql/
├── etl.py
├── load_to_sqlite.py
├── run_etl.ps1
├── requirements.txt
├── README.md
└── data/
    └── app.db
~~~

---

## Quickstart

### 1. 패키지 설치

~~~bash
pip install -r requirements.txt
~~~

### 2. 환경변수 설정

레포 루트에 `.env` 파일을 만들고 DB 저장 경로를 설정합니다.

EDA 대시보드 프로젝트와 함께 사용할 경우:

~~~text
APP_DB_PATH=../project-eda-dashboard/data/app.db
~~~

ETL 프로젝트 내부에 DB를 둘 경우:

~~~text
APP_DB_PATH=./data/app.db
~~~

`.env` 파일은 개인 로컬 설정이므로 커밋하지 않는 것을 권장합니다.

### 3. ETL 실행

~~~bash
python etl.py
python load_to_sqlite.py
~~~

Windows 환경에서 `py` 명령어를 사용하는 경우:

~~~bash
py etl.py
py load_to_sqlite.py
~~~

---

## 결과 확인

SQLite에서 다음 쿼리로 적재 결과를 확인할 수 있습니다.

~~~sql
SELECT COUNT(*) AS n_rows
FROM logs_road;

SELECT date, hour, speed
FROM logs_road
ORDER BY date DESC, hour DESC
LIMIT 10;
~~~

---

## EDA 대시보드와 연결

이 ETL 프로젝트에서 생성한 SQLite DB는 EDA 대시보드 프로젝트에서 사용됩니다.

연동 구조는 다음과 같습니다.

~~~text
project-etl-sql
└── 데이터 수집/정제/적재
        ↓
project-eda-dashboard
└── SQLite DB 조회 → AM/PM KPI 계산 → Streamlit 시각화
~~~

대시보드 프로젝트에서 같은 DB 파일을 바라보도록 경로를 맞추면 ETL 결과가 바로 시각화에 반영됩니다.

---

## 자동화

Windows 작업 스케줄러를 사용하면 ETL을 매일 자동 실행할 수 있습니다.

예시:

~~~bash
schtasks /Create /SC DAILY /ST 06:50 /TN "Road ETL daily" ^
/TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""%USERPROFILE%\Desktop\project-etl-sql\run_etl.ps1""" ^
/RL LIMITED
~~~

자동화 시에는 `run_etl.ps1` 안의 경로가 실제 프로젝트 위치와 일치하는지 확인해야 합니다.

---

## 트러블슈팅

### `no such table: logs_road`

SQLite DB 안에 `logs_road` 테이블이 없을 때 발생합니다.

해결 방법:

- `load_to_sqlite.py`가 정상 실행되었는지 확인
- `APP_DB_PATH`가 올바른 DB 파일을 가리키는지 확인
- EDA 대시보드와 ETL 프로젝트가 같은 DB 파일을 바라보는지 확인

### `unable to open database file`

DB 파일 경로가 잘못되었거나 부모 폴더가 없을 때 발생합니다.

해결 방법:

- `data/` 폴더가 존재하는지 확인
- `.env`의 `APP_DB_PATH` 경로 확인
- 상대경로가 현재 실행 위치 기준으로 맞는지 확인

### 데이터가 중복되는 경우

`(date, hour)` 기준 중복 처리 로직이 정상 적용되는지 확인합니다.

해결 방법:

- 테이블의 유니크 키 설정 확인
- `load_to_sqlite.py`의 upsert 로직 확인
- 같은 날짜와 시간 데이터가 반복 적재되는지 확인

---

## 프로젝트에서 보여주고자 한 역량

- Python 기반 ETL 파이프라인 구현
- Pandas를 활용한 데이터 정제와 표준화
- SQLite 테이블 설계 및 데이터 적재
- 환경변수를 활용한 로컬 실행 환경 분리
- 대시보드 프로젝트와 연결되는 데이터 공급 구조 설계
- 반복 실행과 자동화를 고려한 데이터 파이프라인 구성

---

## 향후 개선 방향

- 실제 공공데이터 API 연동
- 로그 파일 저장 기능 추가
- 적재 실패 시 예외 처리 강화
- 날짜 범위 기반 재적재 기능 추가
- ETL 실행 결과 요약 리포트 생성
- GitHub Actions 기반 자동 실행 실험
