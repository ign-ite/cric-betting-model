from collections import defaultdict

# Match-specific contributions
player_batting_scores = defaultdict(list)  # player -> [scores]
player_bowling_wickets = defaultdict(list)  # player -> [wickets]

player_of_match_count = defaultdict(int)

def update_player_stats(match):
    from collections import Counter

    for inning in match.get("innings", []):
        team = inning.get("team")
        for over in inning.get("overs", []):
            for delivery in over.get("deliveries", []):
                batter = delivery.get("batter")
                bowler = delivery.get("bowler")
                runs = delivery.get("runs", {}).get("batter", 0)
                wicket = delivery.get("wickets", [])

                if batter:
                    player_batting_scores[batter].append(runs)

                if wicket:
                    # Count dismissal against bowler
                    player_bowling_wickets[bowler].append(1)
                else:
                    player_bowling_wickets[bowler].append(0)

    # Track PoM stats
    for pom in match.get("info", {}).get("player_of_match", []):
        player_of_match_count[pom] += 1

def get_batting_avg(player, recent_n=5):
    scores = player_batting_scores.get(player, [])[-recent_n:]
    return sum(scores) / len(scores) if scores else 0

def get_bowling_avg(player, recent_n=5):
    wickets = player_bowling_wickets.get(player, [])[-recent_n:]
    return sum(wickets) / len(wickets) if wickets else 0

def get_form_score(player):
    """Composite form score: avg_runs + wickets + PoM frequency"""
    bat = get_batting_avg(player)
    bowl = get_bowling_avg(player)
    pom_boost = player_of_match_count.get(player, 0) * 0.1  # Scaled
    return bat + bowl + pom_boost

def get_team_form_score(players):
    return sum(get_form_score(p) for p in players)

def reset_trackers():
    player_batting_scores.clear()
    player_bowling_wickets.clear()
    player_of_match_count.clear()
