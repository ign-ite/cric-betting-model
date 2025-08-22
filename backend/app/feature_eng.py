import os
import json
import pandas as pd
from collections import defaultdict, deque
from player_tracker import update_player_stats, get_team_form_score, reset_trackers

# Directory where Cricsheet T20 JSON files are stored
T20_DATA_DIR = "data"

# How many recent matches to consider for win % or avg runs
RECENT_MATCH_WINDOW = 5

def load_all_matches(data_dir):
    matches = []
    for fname in os.listdir(data_dir):
        if fname.endswith(".json"):
            with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
                match = json.load(f)
                if match.get("info", {}).get("match_type") == "T20":
                    matches.append(match)
    return matches

def extract_basic_metadata(match):
    info = match["info"]
    teams = info.get("teams", ["?", "?"])

    competition = info.get("competition")
    if not competition:
        competition = info.get("event", {}).get("name", "Unknown")

    return {
        "teamA": teams[0],
        "teamB": teams[1],
        "winner": info.get("outcome", {}).get("winner", "No Result"),
        "venue": info.get("venue", "Unknown"),
        "date": info.get("dates", ["?"])[0],
        "toss_winner": info.get("toss", {}).get("winner", "Unknown"),
        "toss_decision": info.get("toss", {}).get("decision", "Unknown"),
        "competition": competition
    }

def compute_total_runs(match, team):
    total = 0
    for inning in match.get("innings", []):
        if inning.get("team") == team:
            for over in inning.get("overs", []):
                for delivery in over.get("deliveries", []):
                    total += delivery.get("runs", {}).get("total", 0)
    return total

def feature_engineering(matches):
    data = []

    # History trackers
    team_wins = defaultdict(list)
    team_runs = defaultdict(list)
    team_conceded = defaultdict(list)
    h2h_tracker = defaultdict(lambda: defaultdict(list))
    venue_wins = defaultdict(lambda: defaultdict(int))
    toss_stats = defaultdict(lambda: [0, 0])  # [toss_wins, match_wins]
    bat_first_outcomes = [0, 0]  # [bat first wins, total]

    reset_trackers()

    for match in matches:
        meta = extract_basic_metadata(match)
        A, B = meta['teamA'], meta['teamB']
        venue = meta['venue']
        winner = meta['winner']
        toss_winner = meta['toss_winner']
        toss_decision = meta['toss_decision']

        # Update player stats before computing form features
        update_player_stats(match)

        players = match.get("info", {}).get("players", {})
        teamA_players = players.get(A, [])
        teamB_players = players.get(B, [])
        teamA_form_score = get_team_form_score(teamA_players)
        teamB_form_score = get_team_form_score(teamB_players)

        # Recent win pct
        teamA_recent_wins = sum(team_wins[A][-RECENT_MATCH_WINDOW:])
        teamB_recent_wins = sum(team_wins[B][-RECENT_MATCH_WINDOW:])
        teamA_win_pct = teamA_recent_wins / min(len(team_wins[A]), RECENT_MATCH_WINDOW) if team_wins[A] else 0.5
        teamB_win_pct = teamB_recent_wins / min(len(team_wins[B]), RECENT_MATCH_WINDOW) if team_wins[B] else 0.5

        # H2H win %
        h2h_wins = sum(h2h_tracker[A][B])
        h2h_total = len(h2h_tracker[A][B])
        h2h_pct = h2h_wins / h2h_total if h2h_total > 0 else 0.5

        # Avg runs scored
        avg_runs_A = sum(team_runs[A][-RECENT_MATCH_WINDOW:]) / min(len(team_runs[A]), RECENT_MATCH_WINDOW) if team_runs[A] else 150
        avg_runs_B_conceded = sum(team_conceded[B][-RECENT_MATCH_WINDOW:]) / min(len(team_conceded[B]), RECENT_MATCH_WINDOW) if team_conceded[B] else 160

        avg_runs_B = sum(team_runs[B][-RECENT_MATCH_WINDOW:]) / min(len(team_runs[B]), RECENT_MATCH_WINDOW) if team_runs[B] else 150
        avg_runs_A_conceded = sum(team_conceded[A][-RECENT_MATCH_WINDOW:]) / min(len(team_conceded[A]), RECENT_MATCH_WINDOW) if team_conceded[A] else 160

        # Venue win %
        venue_A_wins = venue_wins[venue].get(A, 0)
        venue_B_wins = venue_wins[venue].get(B, 0)
        total_at_venue = sum(venue_wins[venue].values())
        venue_A_pct = venue_A_wins / total_at_venue if total_at_venue else 0.5
        venue_B_pct = venue_B_wins / total_at_venue if total_at_venue else 0.5

        # Toss impact
        toss_total, toss_match_wins = toss_stats[toss_winner]
        toss_win_rate = toss_match_wins / toss_total if toss_total else 0.5

        # Batting first win rate
        bat_first_team = A if toss_winner == B else B if toss_decision == "field" else toss_winner
        bat_first_wins, bat_first_total = bat_first_outcomes
        bat_first_win_pct = bat_first_wins / bat_first_total if bat_first_total else 0.5

        # Toss match alignment
        toss_match_teamA = 1 if toss_decision == "bat" and teamA_win_pct > 0.5 else 0
        toss_match_teamB = 1 if toss_decision == "bat" and teamB_win_pct > 0.5 else 0

        is_home = 1 if A.lower() in venue.lower() else 0

        data.append({
            **meta,
            "teamA_win_pct_last5": teamA_win_pct,
            "teamB_win_pct_last5": teamB_win_pct,
            "teamA_vs_teamB_h2h": h2h_pct,
            "teamA_avg_runs_scored": avg_runs_A,
            "teamB_avg_runs_conceded": avg_runs_B_conceded,
            "teamB_avg_runs_scored": avg_runs_B,
            "teamA_avg_runs_conceded": avg_runs_A_conceded,
            "venue_win_bias_teamA": venue_A_pct,
            "venue_win_bias_teamB": venue_B_pct,
            "toss_helped_win_rate": toss_win_rate,
            "batting_first_win_pct": bat_first_win_pct,
            "toss_decision_match_teamA": toss_match_teamA,
            "toss_decision_match_teamB": toss_match_teamB,
            "is_home_teamA": is_home,
            "teamA_form_score": teamA_form_score,
            "teamB_form_score": teamB_form_score,
            "match_winner_teamA": 1 if winner == A else 0
        })

        # Update history trackers
        team_wins[A].append(1 if winner == A else 0)
        team_wins[B].append(1 if winner == B else 0)
        h2h_tracker[A][B].append(1 if winner == A else 0)

        runs_A = compute_total_runs(match, A)
        runs_B = compute_total_runs(match, B)
        team_runs[A].append(runs_A)
        team_conceded[B].append(runs_A)
        team_runs[B].append(runs_B)
        team_conceded[A].append(runs_B)

        venue_wins[venue][winner] += 1

        toss_stats[toss_winner][0] += 1
        if winner == toss_winner:
            toss_stats[toss_winner][1] += 1

        if winner == bat_first_team:
            bat_first_outcomes[0] += 1
        bat_first_outcomes[1] += 1

    return pd.DataFrame(data)

if __name__ == "__main__":
    all_matches = load_all_matches(T20_DATA_DIR)
    df = feature_engineering(all_matches)
    df.to_csv("t20_features_full.csv", index=False)
    print("Feature dataset saved as t20_features_full.csv")
