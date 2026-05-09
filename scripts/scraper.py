"""
scraper.py  —  IMDb 2024 movie scraper using Selenium

Debug findings (from debug_selectors.py output):
  - Card metadata lives in:  li.ipc-inline-list__item
  - Items per card are:      ['2024', '2h 46m', 'PG-13']  (year, duration, cert)
  - Genre does NOT appear on the search-results page at all.
    It must be scraped from each movie's individual detail page.
  - Rating  → span.ipc-rating-star--rating
  - Votes   → span.ipc-rating-star--voteCount

Strategy:
  Pass 1 — Collect title, duration, rating, votes, and detail-page URL
            from every card on the search results page.
  Pass 2 — Visit each movie's detail page and scrape genre from the
            genre chips (a.ipc-chip > span.ipc-chip__text) that are
            reliably present there.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
import os
import re

# ─── PATHS ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "movies_2024.csv")
GENRE_CSV_DIR = os.path.join(BASE_DIR, "data", "raw", "genre_wise")
os.makedirs(os.path.dirname(RAW_PATH), exist_ok=True)
os.makedirs(GENRE_CSV_DIR, exist_ok=True)

# ─── CHROME OPTIONS ──────────────────────────────────────────────────────────
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=options)
driver.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
)
wait = WebDriverWait(driver, 15)

# ═══════════════════════════════════════════════════════════════════════════════
# PASS 1 — Scrape search results page: title, duration, rating, votes, URL
# ═══════════════════════════════════════════════════════════════════════════════
url = (
    "https://www.imdb.com/search/title/"
    "?title_type=feature&release_date=2024-01-01,2024-12-31"
)
driver.get(url)
time.sleep(6)

# ── Load more cards (5 rounds ≈ 300 movies) ──────────────────────────────────
for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    try:
        load_more = driver.find_element(
            By.XPATH,
            "//button[contains(@class,'ipc-btn') and "
            "(contains(., 'more') or contains(., 'More'))]",
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", load_more)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", load_more)
        time.sleep(3)
    except NoSuchElementException:
        pass
    except Exception:
        pass

cards = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
print(f"Found {len(cards)} movie cards on search page.")

movies_pass1 = []  # [name, duration, rating, votes, detail_url]

for card in cards:

    # ── Title ─────────────────────────────────────────────────────────────────
    try:
        raw = card.find_element(By.CSS_SELECTOR, "h3.ipc-title__text").text.strip()
        name = re.sub(r"^\d+\.\s*", "", raw).strip()
    except Exception:
        name = "Unknown"

    # ── Detail page URL (needed for genre scraping in pass 2) ─────────────────
    detail_url = ""
    try:
        detail_url = card.find_element(
            By.CSS_SELECTOR, "a.ipc-title-link-wrapper"
        ).get_attribute("href")
        # Strip query params — keep only the /title/ttXXXXXXX/ part
        detail_url = re.sub(r"\?.*$", "", detail_url).rstrip("/")
    except Exception:
        pass

    # ── Metadata items: year / duration / certificate ─────────────────────────
    # Confirmed selector from debug: li.ipc-inline-list__item
    # Items order: ['2024', '2h 46m', 'PG-13']
    duration = ""
    try:
        items = card.find_elements(By.CSS_SELECTOR, "li.ipc-inline-list__item")
        for item in items:
            t = item.text.strip()
            # Duration pattern: contains digits followed by h or m
            if re.search(r"\d+h|\d+m", t):
                duration = t
                break
    except Exception:
        pass

    # ── Rating ────────────────────────────────────────────────────────────────
    rating = ""
    try:
        raw = card.find_element(
            By.CSS_SELECTOR, "span.ipc-rating-star--rating"
        ).text.strip()
        rating = raw if re.match(r"^\d+(\.\d+)?$", raw) else ""
    except Exception:
        pass

    # ── Votes ─────────────────────────────────────────────────────────────────
    votes = ""
    try:
        raw = card.find_element(
            By.CSS_SELECTOR, "span.ipc-rating-star--voteCount"
        ).text.strip()
        votes = raw.replace("(", "").replace(")", "").replace(",", "").strip()
    except Exception:
        pass

    if name and name != "Unknown":
        movies_pass1.append([name, duration, rating, votes, detail_url])

print(f"Pass 1 complete: {len(movies_pass1)} movies collected.")
print("Sample durations:", [r[1] for r in movies_pass1[:5]])

# ═══════════════════════════════════════════════════════════════════════════════
# PASS 2 — Visit each movie detail page to scrape Genre
# ═══════════════════════════════════════════════════════════════════════════════
print("\nPass 2: scraping genre from each movie detail page...")
print("This will take a few minutes — one page visit per movie.\n")

def scrape_genre(url: str) -> str:
    """
    Visit a movie detail page and return the first genre chip text.
    Tries multiple selectors in order of reliability.
    """
    if not url:
        return "Unknown"
    try:
        driver.get(url)
        time.sleep(1.5)

        # Selector 1 — genre chip pills (most reliable on detail pages)
        for sel in [
            "a.ipc-chip--on-baseAlt span.ipc-chip__text",
            "a.ipc-chip span.ipc-chip__text",
            "[data-testid='genres'] a span",
            "[data-testid='storyline-genres'] a",
            "div.ipc-chip-list a span",
        ]:
            try:
                els = driver.find_elements(By.CSS_SELECTOR, sel)
                genres = [e.text.strip() for e in els if e.text.strip()]
                if genres:
                    return genres[0]
            except Exception:
                continue

        # Selector 2 — genre links by href pattern
        try:
            els = driver.find_elements(
                By.XPATH,
                "//a[contains(@href,'/search/title/?genres=')]"
            )
            genres = [e.text.strip() for e in els if e.text.strip()]
            if genres:
                return genres[0]
        except Exception:
            pass

    except Exception:
        pass

    return "Unknown"


movies_final = []
total = len(movies_pass1)

for i, (name, duration, rating, votes, detail_url) in enumerate(movies_pass1):
    genre = scrape_genre(detail_url)
    movies_final.append([name, genre, rating, votes, duration])

    # Progress update every 10 movies
    if (i + 1) % 10 == 0 or (i + 1) == total:
        print(f"  [{i+1}/{total}]  {name}  →  genre='{genre}'  duration='{duration}'")

driver.quit()
print(f"\nPass 2 complete. Total movies: {len(movies_final)}")

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD DATAFRAME
# ═══════════════════════════════════════════════════════════════════════════════
df = pd.DataFrame(
    movies_final,
    columns=["Movie Name", "Genre", "Ratings", "Votes", "Duration"]
)

# ── Parse Ratings ─────────────────────────────────────────────────────────────
df["Ratings"] = pd.to_numeric(df["Ratings"], errors="coerce")

# ── Parse Votes (handles K / M suffixes) ─────────────────────────────────────
def _parse_votes(v: str) -> int:
    v = str(v).strip().replace(",", "").replace("(", "").replace(")", "")
    if v.upper().endswith("K"):
        return int(float(v[:-1]) * 1_000)
    if v.upper().endswith("M"):
        return int(float(v[:-1]) * 1_000_000)
    try:
        return int(float(v))
    except ValueError:
        return 0

df["Votes"] = df["Votes"].apply(_parse_votes)

# ── Diagnostic summary ────────────────────────────────────────────────────────
print("\nGenre value counts (top 10):")
print(df["Genre"].value_counts().head(10))
print("\nDuration samples (first 10):")
print(df["Duration"].head(10).tolist())

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE MASTER RAW CSV
# ═══════════════════════════════════════════════════════════════════════════════
df.to_csv(RAW_PATH, index=False)
print(f"\n✅ Master raw CSV saved → {RAW_PATH}  ({len(df)} rows)")

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE GENRE-WISE INDIVIDUAL CSV FILES
# ═══════════════════════════════════════════════════════════════════════════════
genre_groups = df.groupby("Genre")
saved_genres = []
for genre_name, group in genre_groups:
    safe_name = re.sub(r"[^\w\s-]", "", genre_name).strip().replace(" ", "_")
    genre_path = os.path.join(GENRE_CSV_DIR, f"{safe_name}.csv")
    group.to_csv(genre_path, index=False)
    saved_genres.append(safe_name)

print(f"✅ Genre-wise CSVs saved → {GENRE_CSV_DIR}")
print(f"   Genres ({len(saved_genres)}): {', '.join(saved_genres)}")
print()
print(df.head(10).to_string(index=False))
