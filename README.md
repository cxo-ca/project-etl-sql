# 서울 출퇴근 도로속도 ETL

CSV 데이터를 분석용 스키마로 정규화하고 SQLite에 적재하는 Python 실습 프로젝트입니다. 적재한 데이터는 [Streamlit EDA 대시보드](https://github.com/cxo-ca/project-eda-dashboard)에서 AM/PM 평균속도 지표로 확인할 수 있습니다.

## 현재 구현 범위

| 구성 | 동작 | 상태 |
|---|---|---|
| `load_to_sqlite.py` | CSV 인코딩 재시도, 컬럼 정규화, SQLite upsert | 구현 |
| `etl.py` | 서울 교통 API 요청·응답 변환 예시 | 엔드포인트·키·응답 구조 설정이 필요한 템플릿 |
| `run_etl.ps1` | 수집·적재 실행, 로그 저장, 14일 지난 로그 정리 | Windows 실행 경로와 API 설정 필요 |
| 대시보드의 시연 모드 | 최근 14일 AM 08시·PM 18시 샘플 생성 | [별도 저장소](https://github.com/cxo-ca/project-eda-dashboard)의 기능 |

기본 상태에서 실제 공공데이터를 자동 수집하거나 샘플을 생성하지 않습니다. API를 설정하기 전에는 직접 준비한 CSV로 적재 과정을 확인하세요.

## 빠르게 실행하기

모든 명령은 저장소 루트에서 실행합니다.

### 1. 패키지 설치

```bash
python -m pip install -r requirements.txt
```

### 2. 입력 CSV 준비

`data/` 폴더를 만들고 `data/sample.csv`에 아래 **시연용 값**을 저장합니다. 실제 관측 자료가 아닙니다.

```csv
date,hour,speed
20261018,8,28.5
20261018,18,22.0
```

입력 파일은 `data/*.csv`와 `data/raw/*.csv`에서 찾습니다. 다음 형식을 정규화합니다.

- `date, hour, speed`
- `timestamp, value` — 날짜·시간을 timestamp에서 분리
- `일자, 시간/시간대, 속도` 등 일부 한국어 컬럼

표준 날짜는 `YYYYMMDD`, 시간은 0–23의 정수, 속도는 km/h입니다. 현재 적재기는 도로·구간별 키를 보존하지 않으므로, 구간별 원자료는 먼저 날짜·시간별 대표 속도로 집계해야 합니다.

### 3. DB 경로 선택 후 적재

기본 출력은 `./data/app.db`입니다.

```bash
python load_to_sqlite.py
```

대시보드 저장소가 같은 상위 폴더에 있을 때는 환경변수로 같은 DB를 지정합니다.

Bash:

```bash
APP_DB_PATH=../project-eda-dashboard/data/app.db python load_to_sqlite.py
```

PowerShell:

```powershell
$env:APP_DB_PATH = "../project-eda-dashboard/data/app.db"
python load_to_sqlite.py
```

`.env.example`은 설정 값의 예시입니다. **현재 스크립트는 `.env`를 자동으로 읽지 않으므로** 위와 같이 셸 환경변수로 전달해야 합니다. 상대경로는 명령을 실행한 폴더 기준입니다.

최초 실행 시 테이블·유니크 인덱스를 만들고, 동일한 `(date, hour)`가 있으면 속도를 갱신합니다.

## SQLite 스키마와 확인 쿼리

```sql
CREATE TABLE IF NOT EXISTS logs_road (
    date TEXT,
    hour INTEGER,
    speed REAL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_logs_road_date_hour
ON logs_road(date, hour);

SELECT date, hour, speed
FROM logs_road
ORDER BY date DESC, hour DESC
LIMIT 10;
```

같은 날짜·시간에 여러 행을 넣으면 마지막 행의 속도가 남습니다. 이는 구간별 평균을 계산하는 기능이 아닙니다.

## 실제 API 수집기로 확장하기

`etl.py`의 다음 항목을 사용할 데이터셋의 공식 명세에 맞춰 설정해야 합니다.

1. `API_URL`과 `SERVICE_KEY`
2. 요청 파라미터, 응답의 `data/list` 구조와 컬럼 매핑
3. 페이지 종료 조건 — 현재 예시는 최대 5페이지만 시도
4. 시간 값 정규화와 도로·구간별 자료의 집계 기준

설정 후 실행하면 원본 CSV를 `data/raw/road_YYYYMMDD.csv`에 저장합니다.

```bash
python etl.py
python load_to_sqlite.py
```

API 키를 코드에 넣은 채 커밋하지 마세요. 현재 수집기는 예외를 출력하고 종료하므로, 종료 코드만으로 수집 성공을 판단하지 말고 저장된 파일과 로그를 확인해야 합니다.

## 대시보드 연결

1. 이 저장소와 [project-eda-dashboard](https://github.com/cxo-ca/project-eda-dashboard)를 같은 상위 폴더에 준비합니다.
2. `APP_DB_PATH`를 대시보드의 `data/app.db`로 지정하고 CSV를 적재합니다.
3. 대시보드를 실행해 같은 DB 경로를 입력하고 **DB 불러오기**를 누릅니다.
4. 조회 기간에 입력 자료의 날짜가 포함되어 있는지 확인합니다.

대시보드는 DB 또는 `logs_road`가 없으면 샘플을 생성합니다. 실제 자료를 확인하려면 먼저 적재를 끝내고 올바른 DB 경로를 선택하세요.

## Windows 자동 실행

`run_etl.ps1`은 현재 `$env:USERPROFILE\Desktop\project-etl-sql`로 이동합니다. 실제 위치에 맞춰 수정하고 API 설정과 수동 실행을 확인한 뒤 작업 스케줄러에 등록합니다. 로그는 `logs/etl_*.log`에 저장합니다.

## 테스트

적재기 회귀 테스트는 임시 CSV와 SQLite DB를 사용하며 네트워크에 연결하지 않습니다.

```bash
python -m unittest discover -s tests -v
```

최초 적재, 동일 키 갱신, 폴더 없는 DB 파일명, CP949 입력·인코딩 대체 처리, 사용할 컬럼이 없는 입력을 확인합니다.

## 폴더

| 경로 | 내용 |
|---|---|
| `etl.py` | 공공데이터 API 수집 템플릿 |
| `load_to_sqlite.py` | CSV 정규화·SQLite 적재 |
| `run_etl.ps1` | Windows 실행·로그 관리 |
| `sql/analysis.sql` | 조회 쿼리 예시 |
| `tests/` | 적재기 회귀 테스트 |
| `data/` | 사용자가 준비한 입력·실행 시 생성되는 DB, 저장소에 미포함 |

## 향후 개선

실제 API 연동, 입력 값 범위 검증, 도로·구간별 집계 설계, 실패 시 종료 코드 처리와 수집·적재 품질 검증을 보완할 예정입니다.
