CREATE TABLE IF NOT EXISTS fact_kpi_daily(
  date TEXT PRIMARY KEY,
  kpi_name TEXT NOT NULL,
  value REAL NOT NULL,
  unit TEXT DEFAULT 'USD'
);
CREATE TABLE IF NOT EXISTS fact_drivers_daily(
  date TEXT PRIMARY KEY,
  price REAL,
  ad_spend REAL,
  inventory REAL,
  promo_flag INTEGER
);
