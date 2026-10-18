"""Run the CSV loader against temporary files and real SQLite databases."""

import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LOADER = Path(__file__).resolve().parents[1] / "load_to_sqlite.py"


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "data").mkdir()
        self.csv = self.root / "data" / "sample.csv"

    def run_loader(self, db_path="data/app.db"):
        result = subprocess.run(
            [sys.executable, str(LOADER)],
            cwd=self.root,
            env={**os.environ, "APP_DB_PATH": db_path},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("[ERR]", result.stdout)
        return result

    def rows(self, db_path="data/app.db"):
        with sqlite3.connect(self.root / db_path) as conn:
            return conn.execute(
                "SELECT date, hour, speed FROM logs_road ORDER BY date, hour"
            ).fetchall()

    def test_first_run_creates_table_and_loads_csv(self):
        self.csv.write_text(
            "date,hour,speed\n20261018,8,28.5\n20261018,18,22.0\n",
            encoding="utf-8",
        )
        result = self.run_loader()
        self.assertEqual(
            self.rows(), [("20261018", 8, 28.5), ("20261018", 18, 22.0)]
        )
        self.assertIn("unique rows increased: +2", result.stdout)

    def test_repeated_key_updates_without_adding_a_row(self):
        self.csv.write_text("date,hour,speed\n20261018,8,28.5\n", encoding="utf-8")
        self.run_loader()
        self.csv.write_text("date,hour,speed\n20261018,8,31.0\n", encoding="utf-8")
        result = self.run_loader()
        self.assertEqual(self.rows(), [("20261018", 8, 31.0)])
        self.assertIn("unique rows increased: +0", result.stdout)

    def test_database_filename_without_parent_directory(self):
        self.csv.write_text("date,hour,speed\n20261018,8,28.5\n", encoding="utf-8")
        self.run_loader("app.db")
        self.assertEqual(self.rows("app.db"), [("20261018", 8, 28.5)])

    def test_cp949_korean_columns(self):
        self.csv.write_text("일자,시간,속도\n20261018,8,28.5\n", encoding="cp949")
        self.run_loader()
        self.assertEqual(self.rows(), [("20261018", 8, 28.5)])

    def test_encoding_fallback_uses_supported_pandas_option(self):
        self.csv.write_bytes(
            b"timestamp,value,note\n2026-10-18 08:00:00,28.5,\xff\n"
        )
        self.run_loader()
        self.assertEqual(self.rows(), [("20261018", 8, 28.5)])

    def test_unusable_csv_produces_empty_table_and_statistics(self):
        self.csv.write_text("other\nignored\n", encoding="utf-8")
        result = self.run_loader()
        self.assertEqual(self.rows(), [])
        self.assertIn("[SKIP]", result.stdout)
        self.assertIn("COUNT=0", result.stdout)


if __name__ == "__main__":
    unittest.main()
