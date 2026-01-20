import csv
import os
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_game_history():
    """Load all games from CSV."""
    filepath = os.path.join(DATA_DIR, 'game_history.csv')
    games = []
    if os.path.exists(filepath):
        with open(filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['score1'] = int(row['score1'])
                row['score2'] = int(row['score2'])
                row['season'] = int(row['season'])
                row['week'] = int(row['week'])
                games.append(row)
    return games


def load_season_history():
    """Load season championship history from CSV."""
    filepath = os.path.join(DATA_DIR, 'season_history.csv')
    seasons = []
    if os.path.exists(filepath):
        with open(filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['season'] = int(row['season'])
                seasons.append(row)
    return sorted(seasons, key=lambda x: x['season'], reverse=True)


def save_game(season, week, team1, team2, score1, score2):
    """Add a game to history."""
    filepath = os.path.join(DATA_DIR, 'game_history.csv')
    file_exists = os.path.exists(filepath)

    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['season', 'week', 'team1', 'team2', 'score1', 'score2'])
        writer.writerow([season, week, team1, team2, score1, score2])


def save_season(season, champion, runner_up, heisman, heisman_team):
    """Add a season to history."""
    filepath = os.path.join(DATA_DIR, 'season_history.csv')
    file_exists = os.path.exists(filepath)

    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['season', 'champion', 'runner_up', 'heisman', 'heisman_team'])
        writer.writerow([season, champion, runner_up, heisman, heisman_team])


def get_standings(season=None):
    """Calculate W-L records from game history."""
    games = load_game_history()
    if season:
        games = [g for g in games if g['season'] == season]

    records = defaultdict(lambda: {'wins': 0, 'losses': 0, 'points_for': 0, 'points_against': 0})

    for game in games:
        t1, t2 = game['team1'], game['team2']
        s1, s2 = game['score1'], game['score2']

        records[t1]['points_for'] += s1
        records[t1]['points_against'] += s2
        records[t2]['points_for'] += s2
        records[t2]['points_against'] += s1

        if s1 > s2:
            records[t1]['wins'] += 1
            records[t2]['losses'] += 1
        else:
            records[t2]['wins'] += 1
            records[t1]['losses'] += 1

    # Sort by wins, then point differential
    sorted_teams = sorted(
        records.items(),
        key=lambda x: (x[1]['wins'], x[1]['points_for'] - x[1]['points_against']),
        reverse=True
    )
    return sorted_teams


def get_head_to_head(team1, team2):
    """Get head-to-head record between two teams."""
    games = load_game_history()
    results = {'team1': team1, 'team2': team2, 'team1_wins': 0, 'team2_wins': 0, 'games': []}

    for game in games:
        if (game['team1'] == team1 and game['team2'] == team2):
            results['games'].append(game)
            if game['score1'] > game['score2']:
                results['team1_wins'] += 1
            else:
                results['team2_wins'] += 1
        elif (game['team1'] == team2 and game['team2'] == team1):
            results['games'].append(game)
            if game['score1'] > game['score2']:
                results['team2_wins'] += 1
            else:
                results['team1_wins'] += 1

    return results


def get_team_history(team):
    """Get all games for a specific team."""
    games = load_game_history()
    team_games = []

    for game in games:
        if game['team1'] == team or game['team2'] == team:
            # Normalize so requested team is always "team"
            if game['team1'] == team:
                result = 'W' if game['score1'] > game['score2'] else 'L'
                team_games.append({
                    'season': game['season'],
                    'week': game['week'],
                    'opponent': game['team2'],
                    'score': f"{game['score1']}-{game['score2']}",
                    'result': result
                })
            else:
                result = 'W' if game['score2'] > game['score1'] else 'L'
                team_games.append({
                    'season': game['season'],
                    'week': game['week'],
                    'opponent': game['team1'],
                    'score': f"{game['score2']}-{game['score1']}",
                    'result': result
                })

    return team_games


def get_championships():
    """Get championship history."""
    return load_season_history()


def get_all_seasons():
    """Get list of all seasons in the data."""
    games = load_game_history()
    seasons = set(g['season'] for g in games)
    return sorted(seasons, reverse=True)
