import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ESPN IPL base fixture URLs (2015–2024 known league codes)
IPL_SERIES = [
    ("IPL 2024", "https://www.espncricinfo.com/series/ipl-2024-1415613/match-schedule-fixtures"),
    ("IPL 2023", "https://www.espncricinfo.com/series/ipl-2023-1345038/match-schedule-fixtures"),
    ("IPL 2022", "https://www.espncricinfo.com/series/ipl-2022-1298423/match-schedule-fixtures"),
    ("IPL 2021", "https://www.espncricinfo.com/series/ipl-2021-1249214/match-schedule-fixtures"),
    ("IPL 2020", "https://www.espncricinfo.com/series/ipl-2020-21-1210595/match-schedule-fixtures"),
    ("IPL 2019", "https://www.espncricinfo.com/series/ipl-2019-1165643/match-schedule-fixtures"),
    ("IPL 2018", "https://www.espncricinfo.com/series/ipl-2018-1131611/match-schedule-fixtures"),
]

HEADERS = {"User-Agent": "Mozilla/5.0"}


def load_cricsheet_matches(folder):
    matches = []
    for fname in os.listdir(folder):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(folder, fname), 'r', encoding='utf-8') as f:
            data = json.load(f)
            info = data.get("info", {})
            comp = info.get("competition") or info.get("event", {}).get("name", "")
            if "IPL" in comp:
                matches.append({
                    "date": info.get("dates", ["?"])[0],
                    "teams": info.get("teams", ["?", "?"]),
                    "venue": info.get("venue", "Unknown"),
                    "match": data
                })
    return matches


def standardize_team_name(name):
    replacements = {
        "Delhi Capitals": "Delhi",
        "Delhi Daredevils": "Delhi",
        "Punjab Kings": "Punjab",
        "Kings XI Punjab": "Punjab",
        "Royal Challengers Bangalore": "Bangalore",
        "Rajasthan Royals": "Rajasthan",
        "Chennai Super Kings": "Chennai",
        "Mumbai Indians": "Mumbai",
        "Kolkata Knight Riders": "Kolkata",
        "Sunrisers Hyderabad": "Hyderabad",
        "Gujarat Titans": "Gujarat",
        "Lucknow Super Giants": "Lucknow",
        "Rising Pune Supergiants": "Pune",
        "Pune Warriors": "Pune"
    }
    return replacements.get(name, name)


def match_teams_date(match_date, team1, team2, html):
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.find_all('a', href=True)

    for a in cards:
        href = a['href']
        text = a.get_text().strip()
        if not ("vs" in text and "/full-scorecard" in href):
            continue

        # Extract teams
        parts = text.split("vs")
        if len(parts) != 2:
            continue
        t1 = standardize_team_name(parts[0].strip())
        t2 = standardize_team_name(parts[1].split(',')[0].strip())

        if sorted([t1, t2]) != sorted([team1, team2]):
            continue

        # Attempt to match by date in URL if present
        match_id = href.strip('/').split('-')[-1]
        if match_id.isdigit():
            return match_id
    return None


def map_cricsheet_to_espn(folder):
    cricsheet_matches = load_cricsheet_matches(folder)
    print(f"Found {len(cricsheet_matches)} IPL matches from Cricsheet")

    match_id_map = {}

    for series_name, series_url in IPL_SERIES:
        print(f"Fetching fixtures from {series_name}...")
        try:
            res = requests.get(series_url, headers=HEADERS, timeout=10)
            if res.status_code != 200:
                print(f"[WARN] Could not fetch {series_url}")
                continue

            html = res.text
            for match in cricsheet_matches:
                date = match['date']
                team1 = standardize_team_name(match['teams'][0])
                team2 = standardize_team_name(match['teams'][1])
                key = f"{team1}_vs_{team2}_{date}"

                if key in match_id_map:
                    continue  # already found

                match_id = match_teams_date(date, team1, team2, html)
                if match_id:
                    match_id_map[key] = match_id

        except Exception as e:
            print(f"[ERROR] Failed to parse {series_name}: {e}")

    with open("ipl_match_id_map.json", "w") as f:
        json.dump(match_id_map, f, indent=2)
    print(f"Saved {len(match_id_map)} match IDs to ipl_match_id_map.json")


if __name__ == "__main__":
    map_cricsheet_to_espn("data")
