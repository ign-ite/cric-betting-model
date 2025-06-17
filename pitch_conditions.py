import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Expanded keywords mapping to pitch type
PITCH_KEYWORDS = {
    "spin": ["turn", "dry", "slow", "dust", "crumble", "grip", "assists spinners", "spin-friendly", "spin"],
    "seam": ["green", "seam", "grass", "bounce", "carry", "movement", "new ball", "pace"],
    "batting": ["flat", "good for batting", "true bounce", "run fest", "high scoring", "batting paradise", "plenty of runs"],
    "balanced": ["balanced", "even contest"]
}

def fallback_espn_search(venue):
    query = quote_plus(f"{venue} pitch report site:espncricinfo.com")
    search_url = f"https://www.espncricinfo.com/search/_/q/{query}"
    print(f"[DEBUG] Using fallback ESPNcricinfo search: {search_url}")

    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.find_all("a"):
            href = a.get("href")
            if href and "pitch" in href and href.startswith("https://"):
                links.append(href)
        return links[:3]
    except Exception as e:
        print(f"[ERROR] Fallback ESPN search failed: {e}")
        return []

def fetch_pitch_text(url):
    try:
        page = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(page.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        text = text.lower()
        print(f"[DEBUG] Text extracted from {url} (first 500 chars):\n{text[:500]}\n")
        return text
    except Exception as e:
        print(f"[ERROR] Failed to fetch or parse {url}: {e}")
        return ""

def classify_pitch_type(text):
    scores = {k: 0 for k in PITCH_KEYWORDS}
    for category, keywords in PITCH_KEYWORDS.items():
        for kw in keywords:
            scores[category] += text.count(kw)

    print("[DEBUG] Keyword match scores:", scores)

    if all(v == 0 for v in scores.values()):
        return "unknown"

    return max(scores.items(), key=lambda x: x[1])[0]

def get_pitch_type(date, venue):
    if isinstance(date, datetime.date):
        date_str = date.strftime("%Y-%m-%d")
    else:
        date_str = str(date)

    print("[INFO] Attempting direct ESPN fallback scraping...")
    article_urls = fallback_espn_search(venue)
    for url in article_urls:
        text = fetch_pitch_text(url)
        pitch_type = classify_pitch_type(text)
        if pitch_type != "unknown":
            return pitch_type

    return "unknown"

# Example usage:
pitch_type = get_pitch_type("2022-10-23", "Melbourne Cricket Ground")
print("Predicted pitch type:", pitch_type)
