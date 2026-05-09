"""
debug_selectors.py  —  Run this ONCE to find IMDb's real CSS selectors.
It opens the browser, loads IMDb, saves the first card's full HTML to
data/raw/debug_card.html, AND prints every span/li/div text inside the
card so you can see exactly what text is available and under what tags.

Run with:
    python scripts/debug_selectors.py
Then open data/raw/debug_card.html in your browser and inspect it.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG_HTML = os.path.join(BASE_DIR, "data", "raw", "debug_card.html")
os.makedirs(os.path.dirname(DEBUG_HTML), exist_ok=True)

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=options)
driver.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
)

url = (
    "https://www.imdb.com/search/title/"
    "?title_type=feature&release_date=2024-01-01,2024-12-31"
)
driver.get(url)
time.sleep(6)

cards = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
print(f"Found {len(cards)} cards on page.")

if not cards:
    print("ERROR: No cards found. IMDb may have blocked the request. Try again.")
    driver.quit()
    exit()

# ── Save first card's full HTML ───────────────────────────────────────────────
card = cards[0]
html = driver.execute_script("return arguments[0].outerHTML;", card)
with open(DEBUG_HTML, "w", encoding="utf-8") as f:
    f.write("<html><body>\n")
    f.write(html)
    f.write("\n</body></html>")
print(f"✅ Full card HTML saved → {DEBUG_HTML}")
print("   Open this file in your browser and press F12 to inspect.\n")

# ── Print ALL text nodes inside the first card with their tag + classes ───────
print("=" * 70)
print("ALL elements with text inside card[0]:")
print("=" * 70)
all_els = card.find_elements(By.XPATH, ".//*")
for el in all_els:
    try:
        txt = el.text.strip()
        if not txt or "\n" in txt:
            continue
        tag = el.tag_name
        cls = el.get_attribute("class") or ""
        tid = el.get_attribute("data-testid") or ""
        print(f"  <{tag}> class='{cls[:60]}'  testid='{tid}'  →  '{txt}'")
    except Exception:
        pass

# ── Specifically probe the selectors we care about ───────────────────────────
print("\n" + "=" * 70)
print("PROBING specific selectors on ALL cards (first 5 cards):")
print("=" * 70)
selectors_to_probe = [
    "span[data-testid='title-metadata-item']",
    "span.dli-title-metadata-item",
    "span.ipc-inline-list__item",
    "li.ipc-inline-list__item",
    "a.ipc-chip span",
    "span.genre",
    "[data-testid='genre-tag']",
    "a[href*='genre'] span",
    "a[href*='genres'] span",
]

for sel in selectors_to_probe:
    hits = []
    for c in cards[:5]:
        try:
            els = c.find_elements(By.CSS_SELECTOR, sel)
            for e in els:
                t = e.text.strip()
                if t:
                    hits.append(t)
        except Exception:
            pass
    if hits:
        print(f"  FOUND  '{sel}'  → {hits[:8]}")
    else:
        print(f"  NONE   '{sel}'")

driver.quit()
print("\nDone. Use the results above to identify the correct selectors.")
