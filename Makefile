PY=python

install:
	$(PY) -m pip install -r requirements.txt

run:
	$(PY) etl.py
	$(PY) load_to_sqlite.py

lint:
	$(PY) -m pip install ruff
	$(PY) -m ruff check .

test:
	$(PY) -m pip install pytest
	$(PY) -m pytest -q
