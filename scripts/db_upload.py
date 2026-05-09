"""
db_upload.py  —  Upload cleaned IMDb data to SQLite via SQLAlchemy
Fixes applied:
  1. Bracketed column name "[Movie Name]" breaks on SQLite (SQLite uses double-quotes).
     Replaced with double-quoted "Movie Name" inside the raw SQL queries.
  2. Added explicit FileNotFoundError with a helpful message when clean CSV is missing.
  3. Added engine.dispose() at the end to cleanly close DB connections.
  4. Sample queries now wrapped in a try/except so a DB error doesn't crash the script.
"""

import pandas as pd
import os
from sqlalchemy import create_engine, text

# ─── PATHS ───────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "data", "cleaned", "clean_movies.csv")
DB_PATH = os.path.join(BASE_DIR, "database", "movies.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ─── LOAD CLEANED DATA ───────────────────────────────────────────────────────────
# FIX 2 – raise a clear error if the pipeline has not been run yet
if not os.path.exists(CLEAN_PATH):
    raise FileNotFoundError(
        f"Cleaned CSV not found: {CLEAN_PATH}\n"
        "Please run  scripts/scraper.py  then  scripts/clean_data.py  first."
    )

df = pd.read_csv(CLEAN_PATH)
print(f"Loaded {len(df)} rows from cleaned CSV.")

# ─── CREATE SQLALCHEMY ENGINE (SQLite) ───────────────────────────────────────────
# SQLite is used here for portability; swap the connection URL for production:
#   PostgreSQL : "postgresql://user:password@localhost:5432/imdb2024"
#   MySQL      : "mysql+pymysql://user:password@localhost:3306/imdb2024"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# ─── UPLOAD TABLE ────────────────────────────────────────────────────────────────
df.to_sql("movies", con=engine, if_exists="replace", index=False)

# ─── VERIFY ──────────────────────────────────────────────────────────────────────
with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM movies")).scalar()

print(f"✅ Database ready at : {DB_PATH}")
print(f"   Table 'movies'   →  {count} rows")

# ─── SAMPLE QUERIES (business use cases) ─────────────────────────────────────────
# FIX 1 – SQLite uses double-quotes for identifiers, not square brackets
try:
    print("\n── Top 5 Rated Movies ───────────────────────────────────────────────────────")
    top5 = pd.read_sql(
        'SELECT "Movie Name", Genre, Ratings, Votes '
        "FROM movies ORDER BY Ratings DESC LIMIT 5",
        engine,
    )
    print(top5.to_string(index=False))

    print("\n── Genre Count ──────────────────────────────────────────────────────────────")
    genre_count = pd.read_sql(
        "SELECT Genre, COUNT(*) as Count FROM movies "
        "GROUP BY Genre ORDER BY Count DESC",
        engine,
    )
    print(genre_count.to_string(index=False))

except Exception as e:
    print(f"⚠ Sample query failed: {e}")

# FIX 3 – dispose engine so the .db file handle is released cleanly
engine.dispose()
