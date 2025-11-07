# forecastfactory/forecastfactory/io_sql.py
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import pandas as pd
from pathlib import Path

def get_engine(url: str) -> Engine:
    return create_engine(url, future=True)

def _read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def init_demo(engine: Engine):
    """
    Load db/schema.sql and db/seed.sql.
    - For SQLite: use executescript (allows multiple statements).
    - For other DBs: split on ';' and execute sequentially.
    """
    base = Path(__file__).resolve().parent.parent  # project root
    schema_path = (base / "db" / "schema.sql")
    seed_path   = (base / "db" / "seed.sql")

    backend = engine.url.get_backend_name()

    if backend == "sqlite":
        # Use DB-API executescript (multiple statements allowed)
        raw = engine.raw_connection()
        try:
            cur = raw.cursor()
            cur.executescript(_read_file(schema_path))
            cur.executescript(_read_file(seed_path))
            raw.commit()
        finally:
            raw.close()
    else:
        # Generic path: split into individual statements and run each
        def exec_many(sql_text: str):
            # naive split; skips empty lines/fragments
            for stmt in sql_text.split(";"):
                s = stmt.strip()
                if s:
                    with engine.begin() as con:
                        con.exec_driver_sql(s)

        exec_many(_read_file(schema_path))
        exec_many(_read_file(seed_path))

def read_tables(engine: Engine):
    with engine.begin() as con:
        kpi = pd.read_sql(text("SELECT * FROM fact_kpi_daily ORDER BY date"), con)
        drv = pd.read_sql(text("SELECT * FROM fact_drivers_daily ORDER BY date"), con)
    kpi["date"] = pd.to_datetime(kpi["date"])
    drv["date"] = pd.to_datetime(drv["date"])
    return kpi, drv
