일 1회 자동 수집 → SQLite 적재, 주간 리포트 5분 내 생성
https://sites.google.com/view/cxo-ca
etl, sql, python, sqlite, automation

ETL: Daily ETL → load to SQLite, weekly report in 5 min

cd ..
git clone git@github.com:cxo-ca/project-etl-sql.git
cd project-etl-sql

python -m venv .venv
# Win: . .venv/Scripts/activate | macOS/Linux: source .venv/bin/activate
pip install pandas requests sqlalchemy sqlite-utils
pip freeze > requirements.txt

mkdir -p data sql
cat > etl.py << 'PY'
import pandas as pd, os
from datetime import datetime
os.makedirs("data", exist_ok=True)
df = pd.DataFrame({"date":[datetime.now().strftime("%Y-%m-%d")]*5,"value":[1,2,3,4,5]})
out = f"data/sample_{datetime.now().strftime('%Y%m%d')}.csv"
df.to_csv(out, index=False)
print(f"Wrote {out}")
PY
printf ".venv/\n__pycache__/\n*.db\n*.DS_Store\n" > .gitignore

git add requirements.txt etl.py sql .gitignore
git commit -m "chore: ETL 스켈레톤/의존성/폴더 구조 추가"
git push
