"""
clean_data.py  —  Data cleaning pipeline for IMDb 2024 dataset
"""

import pandas as pd
import os
import re

# ─── PATHS ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "movies_2024.csv")
GENRE_CSV_DIR = os.path.join(BASE_DIR, "data", "raw", "genre_wise")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "cleaned", "clean_movies.csv")
GENRE_CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned", "genre_wise")
os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)
os.makedirs(GENRE_CLEAN_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP A — Merge all genre-wise raw CSVs (fall back to master CSV if needed)
# ═══════════════════════════════════════════════════════════════════════════════
genre_files = (
    [
        os.path.join(GENRE_CSV_DIR, f)
        for f in os.listdir(GENRE_CSV_DIR)
        if f.endswith(".csv")
    ]
    if os.path.isdir(GENRE_CSV_DIR)
    else []
)

if genre_files:
    frames = []
    for gf in genre_files:
        try:
            frames.append(pd.read_csv(gf))
        except Exception as e:
            print(f"  ⚠ Could not read {gf}: {e}")
    df = pd.concat(frames, ignore_index=True)
    print(f"Merged {len(genre_files)} genre-wise CSVs → {len(df)} rows total.")
else:
    df = pd.read_csv(RAW_PATH)
    print(f"No genre-wise CSVs found; loaded master raw CSV → {len(df)} rows.")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP B — Clean each column
# ═══════════════════════════════════════════════════════════════════════════════

# ── Movie Name ────────────────────────────────────────────────────────────────
df["Movie Name"] = df["Movie Name"].astype(str).str.strip()
df["Movie Name"] = df["Movie Name"].replace(r"^\s*$", pd.NA, regex=True)

# ── Ratings ───────────────────────────────────────────────────────────────────
df["Ratings"] = pd.to_numeric(df["Ratings"], errors="coerce")

# ── Votes (handles "1.2K", "3.5M", plain integers) ───────────────────────────
def parse_votes(v) -> int:
    v = str(v).strip().replace(",", "").replace("(", "").replace(")", "")
    if v.upper().endswith("K"):
        return int(float(v[:-1]) * 1_000)
    if v.upper().endswith("M"):
        return int(float(v[:-1]) * 1_000_000)
    try:
        return int(float(v))
    except ValueError:
        return 0

df["Votes"] = df["Votes"].apply(parse_votes)
df["Votes"] = df["Votes"].fillna(0).astype(int)

# ── Duration ("2h 46m" → 166, "1h 44m" → 104, "45m" → 45, "2h" → 120) ──────
def parse_duration(d) -> float:
    """
    Convert any duration string to total minutes (float).
    Returns NaN only when the value is genuinely missing/unparseable —
    never returns 0 as a placeholder.
    Examples:
        "2h 46m" → 166.0
        "1h"     → 60.0
        "45m"    → 45.0
        ""       → NaN
        NaN      → NaN
    """
    if pd.isna(d):
        return float("nan")

    d = str(d).strip()

    # Genuinely empty or missing — return NaN, not zero
    if d in ("", "nan", "None", "0"):
        return float("nan")

    hours_match = re.search(r"(\d+)\s*h", d, re.IGNORECASE)
    mins_match = re.search(r"(\d+)\s*m", d, re.IGNORECASE)

    if hours_match or mins_match:
        h = int(hours_match.group(1)) if hours_match else 0
        m = int(mins_match.group(1)) if mins_match else 0
        total = h * 60 + m
        # Sanity check: a movie duration should be between 1 min and 600 min
        if 1 <= total <= 600:
            return float(total)
        return float("nan")

    # Last resort: bare number — treat as minutes
    bare = re.match(r"^(\d+)$", d)
    if bare:
        val = int(bare.group(1))
        if 1 <= val <= 600:
            return float(val)

    return float("nan")

df["Duration"] = df["Duration"].apply(parse_duration)

# ── Genre ─────────────────────────────────────────────────────────────────────
df["Genre"] = df["Genre"].fillna("Unknown").str.strip()

# ── Drop rows with missing rating or missing name; remove duplicates ──────────
before = len(df)
df = df.dropna(subset=["Ratings", "Movie Name"])
df = df.drop_duplicates(subset=["Movie Name"])
print(
    f"Dropped {before - len(df)} rows "
    f"(missing rating / blank name / duplicates). Remaining: {len(df)}"
)

# ─── Diagnostic ───────────────────────────────────────────────────────────────
dur_available = df["Duration"].notna().sum()
dur_missing   = df["Duration"].isna().sum()
print(f"Duration — available: {dur_available}, missing (NaN): {dur_missing}")
print(f"Genre    — unique values: {df['Genre'].nunique()}")
print(df[['Movie Name','Genre','Ratings','Votes','Duration']].head())

# ═══════════════════════════════════════════════════════════════════════════════
# STEP C — Save master cleaned CSV
# ═══════════════════════════════════════════════════════════════════════════════
df.to_csv(CLEAN_PATH, index=False)
print(f"\n✅ Master cleaned CSV → {CLEAN_PATH}")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP D — Save cleaned genre-wise CSVs
# ═══════════════════════════════════════════════════════════════════════════════
genre_groups = df.groupby("Genre")
saved_genre_names = []
for genre_name, group in genre_groups:
    safe_name = re.sub(r"[^\w\s-]", "", genre_name).strip().replace(" ", "_")
    genre_path = os.path.join(GENRE_CLEAN_DIR, f"{safe_name}_clean.csv")
    group.to_csv(genre_path, index=False)
    saved_genre_names.append(safe_name)

print(
    f"✅ Cleaned genre-wise CSVs → {GENRE_CLEAN_DIR} "
    f"({len(saved_genre_names)} genres)"
)
