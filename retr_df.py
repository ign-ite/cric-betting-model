import os
import json
import pandas as pd

def parse_t20_matches(folder):
    match_data = []

    for fname in os.listdir(folder):
        if fname.endswith(".json"):
            with open(os.path.join(folder, fname), "r", encoding="utf-8") as f:
                try:
                    match = json.load(f)
                    info = match.get("info", {})

                    if info.get("match_type") != "T20":
                        continue

                    teams = info.get("teams", ["?", "?"])
                    winner = info.get("outcome", {}).get("winner", "No Result")
                    toss = info.get("toss", {})
                    venue = info.get("venue", "Unknown")
                    date = info.get("dates", ["?"])[0]
                    competition = info.get("competition", "Unknown")

                    match_data.append({
                        "team_1": teams[0],
                        "team_2": teams[1],
                        "venue": venue,
                        "date": date,
                        "competition": competition,
                        "toss_winner": toss.get("winner", "Unknown"),
                        "toss_decision": toss.get("decision", "Unknown"),
                        "match_winner": winner,
                        "result_given": "winner" in info.get("outcome", {})
                    })

                except Exception as e:
                    print(f"Failed to parse {fname}: {e}")
                    continue

    return pd.DataFrame(match_data)

if __name__ == "__main__":
    df = parse_t20_matches("data")
    print(f"Parsed {len(df)} T20 matches.")
    df1 = df[5]
    print(df1)
    #df.to_csv("t20_match_metadata.csv", index=False)