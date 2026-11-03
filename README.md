# 서울 출퇴근 도로속도 ETL

**서로 다른 CSV 형식을 `date / hour / speed`로 통일하고, SQLite에 중복 없이 갱신 적재하는 개인 프로젝트입니다.**

`Python` · `Pandas` · `SQL` · `SQLite` · `unittest`

[적재 코드](load_to_sqlite.py) · [회귀 테스트 6개](tests/test_loader.py) · [연결 대시보드](https://github.com/cxo-ca/project-eda-dashboard)

## 핵심 구현

| 해결할 문제 | 구현한 처리 | 확인할 코드 |
|---|---|---|
| 입력마다 다른 컬럼·인코딩 | 표준 컬럼, `timestamp/value`, 일부 한국어 컬럼을 정규화하고 UTF-8·CP949 등을 재시도 | [`normalize`, `read_csv_flex`](load_to_sqlite.py) |
| 같은 날짜·시간의 반복 적재 | `(date, hour)` 유니크 키와 SQLite upsert로 기존 속도 갱신 | [`upsert`](load_to_sqlite.py) |
| 실행 결과 확인 | 입력별 처리 행수, 신규 키 증가량, 전체 행수·날짜 범위 출력 | [`main`](load_to_sqlite.py) |
| 환경·입력 차이에 따른 회귀 | 임시 CSV·실제 SQLite DB로 최초 적재, 갱신, 인코딩, 빈 결과 등 6개 테스트 | [`tests/`](tests/) |

분석 화면까지 이어지는 구성은 **CSV → 정규화 → SQLite → [Streamlit 대시보드](https://github.com/cxo-ca/project-eda-dashboard)**입니다. 이 저장소의 완성된 기능은 **CSV 적재기**이며, [`etl.py`](etl.py)의 공공데이터 API 수집기는 주소·키·응답 구조 설정이 필요한 템플릿입니다.

## 빠르게 실행하기

명령은 저장소 루트에서 실행합니다. 아래 CSV는 오늘 날짜로 만드는 **가상 시연 자료**입니다.

```bash
git clone https://github.com/cxo-ca/project-etl-sql.git
cd project-etl-sql
python -m pip install -r requirements.txt
python -c "from pathlib import Path; from datetime import date; Path('data').mkdir(exist_ok=True); d=date.today().strftime('%Y%m%d'); Path('data/sample.csv').write_text(f'date,hour,speed\n{d},8,28.5\n{d},18,22.0\n', encoding='utf-8')"
python load_to_sqlite.py
python -m unittest discover -s tests -v
```

처음 실행하는 빈 DB라면 `data/app.db`에 2행을 저장합니다. 같은 입력을 재실행하면 행수는 늘지 않고 같은 키의 속도가 갱신됩니다.

## 입력·출력 사양

입력은 `data/*.csv`와 `data/raw/*.csv`입니다. 지원하는 대표적인 형식은 다음과 같습니다.

| 입력 컬럼 | 변환 |
|---|---|
| `date, hour, speed` | 날짜의 하이픈 제거, 시간·속도 수치화 |
| `timestamp, value` | timestamp에서 날짜·시간 분리, value를 속도로 변환 |
| `일자, 시간/시간대, 속도` | 일부 한국어 컬럼을 표준명으로 변환 |

출력은 `logs_road(date TEXT, hour INTEGER, speed REAL)`입니다. 예상 형식은 날짜 `YYYYMMDD`, 시간 0–23, 속도 km/h입니다. 수치화할 수 없는 시간·속도 등은 제외하지만, 날짜의 유효성과 시간·속도 범위는 아직 검증하지 않습니다.

```sql
SELECT date, hour, speed
FROM logs_road
ORDER BY date DESC, hour DESC
LIMIT 10;
```

**키는 도로·구간 단위가 아닌 `(date, hour)`입니다.** 같은 키의 여러 행은 마지막 속도로 덮어씁니다. 구간별 원자료는 먼저 날짜·시간별 대표값으로 집계해야 합니다.

## 대시보드 연결

1. 이 저장소와 [project-eda-dashboard](https://github.com/cxo-ca/project-eda-dashboard)를 같은 상위 폴더에 준비합니다.
2. 아래처럼 공통 DB에 먼저 CSV를 적재합니다. 실제 자료에는 기존 시연 DB와 다른 **새 DB 경로**를 사용하면 가상 샘플이 섞이는 일을 피할 수 있습니다.
3. 대시보드를 실행하고 SQLite 경로를 `./data/traffic.db`로 입력한 뒤 **DB 불러오기**를 누릅니다.

Bash:

```bash
APP_DB_PATH=../project-eda-dashboard/data/traffic.db python load_to_sqlite.py
```

PowerShell:

```powershell
$env:APP_DB_PATH = '../project-eda-dashboard/data/traffic.db'
python load_to_sqlite.py
```

상대경로는 명령 실행 폴더 기준입니다. `.env.example`은 예시이며 스크립트는 `.env`를 자동으로 읽지 않습니다. 대시보드는 선택한 DB에 `logs_road`가 없으면 샘플을 생성하므로 **적재를 먼저 완료하고 같은 DB를 선택**해야 합니다.

## API 수집·자동 실행으로 확장하기

<details>
<summary>템플릿 설정과 Windows 실행 안내</summary>

[`etl.py`](etl.py)에서 데이터셋의 공식 명세에 맞춰 다음을 설정합니다.

- `API_URL`, `SERVICE_KEY`, 요청 파라미터와 응답의 `data/list` 구조
- 컬럼 매핑과 시간 값 정규화
- 페이지 종료 조건: 현재 예시는 최대 5페이지
- 도로·구간별 자료를 날짜·시간별로 집계할 기준

설정 후 `python etl.py`로 `data/raw/road_YYYYMMDD.csv`를 만들고, `python load_to_sqlite.py`로 적재합니다. 현재 수집기는 예외를 출력하고 종료하므로 종료 코드만으로 성공을 판단하지 말고 저장 파일·로그를 확인해야 합니다. API 키는 커밋하지 않습니다.

[`run_etl.ps1`](run_etl.ps1)은 수집·적재 실행, `logs/etl_*.log` 저장, 14일 지난 로그 정리를 수행합니다. 현재 작업 경로는 `$env:USERPROFILE\Desktop\project-etl-sql`로 고정되어 있으므로 수정이 필요합니다. API 설정과 수동 실행을 검증한 뒤 Windows 작업 스케줄러에 등록합니다.

</details>

## 검증·개선 범위

- **검증:** 네트워크 없이 실행하는 [6개 적재기 회귀 테스트](tests/test_loader.py). 최초 적재·같은 키 갱신·부모 경로 없는 DB 파일명·CP949·인코딩 대체·사용할 컬럼 없는 입력을 확인합니다.
- **다음 개선:** 실제 API 연동, 날짜·값 범위 검증, 도로별 키·집계 설계, 수집 실패의 종료 코드 처리와 적재 품질 점검.

