# CFB Teams with ESPN logo URLs
# Logo URL format: https://a.espncdn.com/i/teamlogos/ncaa/500/{id}.png

CFB_TEAMS = {
    # SEC
    "Alabama": {"id": 333, "conference": "SEC"},
    "Arkansas": {"id": 8, "conference": "SEC"},
    "Auburn": {"id": 2, "conference": "SEC"},
    "Florida": {"id": 57, "conference": "SEC"},
    "Georgia": {"id": 61, "conference": "SEC"},
    "Kentucky": {"id": 96, "conference": "SEC"},
    "LSU": {"id": 99, "conference": "SEC"},
    "Mississippi State": {"id": 344, "conference": "SEC"},
    "Missouri": {"id": 142, "conference": "SEC"},
    "Oklahoma": {"id": 201, "conference": "SEC"},
    "Ole Miss": {"id": 145, "conference": "SEC"},
    "South Carolina": {"id": 2579, "conference": "SEC"},
    "Tennessee": {"id": 2633, "conference": "SEC"},
    "Texas": {"id": 251, "conference": "SEC"},
    "Texas A&M": {"id": 245, "conference": "SEC"},
    "Vanderbilt": {"id": 238, "conference": "SEC"},

    # Big Ten
    "Illinois": {"id": 356, "conference": "Big Ten"},
    "Indiana": {"id": 84, "conference": "Big Ten"},
    "Iowa": {"id": 2294, "conference": "Big Ten"},
    "Maryland": {"id": 120, "conference": "Big Ten"},
    "Michigan": {"id": 130, "conference": "Big Ten"},
    "Michigan State": {"id": 127, "conference": "Big Ten"},
    "Minnesota": {"id": 135, "conference": "Big Ten"},
    "Nebraska": {"id": 158, "conference": "Big Ten"},
    "Northwestern": {"id": 77, "conference": "Big Ten"},
    "Ohio State": {"id": 194, "conference": "Big Ten"},
    "Oregon": {"id": 2483, "conference": "Big Ten"},
    "Penn State": {"id": 213, "conference": "Big Ten"},
    "Purdue": {"id": 2509, "conference": "Big Ten"},
    "Rutgers": {"id": 164, "conference": "Big Ten"},
    "UCLA": {"id": 26, "conference": "Big Ten"},
    "USC": {"id": 30, "conference": "Big Ten"},
    "Washington": {"id": 264, "conference": "Big Ten"},
    "Wisconsin": {"id": 275, "conference": "Big Ten"},

    # Big 12
    "Arizona": {"id": 12, "conference": "Big 12"},
    "Arizona State": {"id": 9, "conference": "Big 12"},
    "Baylor": {"id": 239, "conference": "Big 12"},
    "BYU": {"id": 252, "conference": "Big 12"},
    "Cincinnati": {"id": 2132, "conference": "Big 12"},
    "Colorado": {"id": 38, "conference": "Big 12"},
    "Houston": {"id": 248, "conference": "Big 12"},
    "Iowa State": {"id": 66, "conference": "Big 12"},
    "Kansas": {"id": 2305, "conference": "Big 12"},
    "Kansas State": {"id": 2306, "conference": "Big 12"},
    "Oklahoma State": {"id": 197, "conference": "Big 12"},
    "TCU": {"id": 2628, "conference": "Big 12"},
    "Texas Tech": {"id": 2641, "conference": "Big 12"},
    "UCF": {"id": 2116, "conference": "Big 12"},
    "Utah": {"id": 254, "conference": "Big 12"},
    "West Virginia": {"id": 277, "conference": "Big 12"},

    # ACC
    "Boston College": {"id": 103, "conference": "ACC"},
    "California": {"id": 25, "conference": "ACC"},
    "Clemson": {"id": 228, "conference": "ACC"},
    "Duke": {"id": 150, "conference": "ACC"},
    "Florida State": {"id": 52, "conference": "ACC"},
    "Georgia Tech": {"id": 59, "conference": "ACC"},
    "Louisville": {"id": 97, "conference": "ACC"},
    "Miami": {"id": 2390, "conference": "ACC"},
    "NC State": {"id": 152, "conference": "ACC"},
    "North Carolina": {"id": 153, "conference": "ACC"},
    "Pittsburgh": {"id": 221, "conference": "ACC"},
    "SMU": {"id": 2567, "conference": "ACC"},
    "Stanford": {"id": 24, "conference": "ACC"},
    "Syracuse": {"id": 183, "conference": "ACC"},
    "Virginia": {"id": 258, "conference": "ACC"},
    "Virginia Tech": {"id": 259, "conference": "ACC"},
    "Wake Forest": {"id": 154, "conference": "ACC"},

    # Other notable teams
    "Notre Dame": {"id": 87, "conference": "Independent"},
    "Army": {"id": 349, "conference": "Independent"},
    "Navy": {"id": 2426, "conference": "AAC"},
    "Memphis": {"id": 235, "conference": "AAC"},
    "Tulane": {"id": 2655, "conference": "AAC"},
    "Boise State": {"id": 68, "conference": "Mountain West"},
    "San Diego State": {"id": 21, "conference": "Mountain West"},
    "Fresno State": {"id": 278, "conference": "Mountain West"},
    "UNLV": {"id": 2439, "conference": "Mountain West"},
    "Liberty": {"id": 2335, "conference": "Conference USA"},
    "James Madison": {"id": 256, "conference": "Sun Belt"},
    "Appalachian State": {"id": 2026, "conference": "Sun Belt"},
    "Coastal Carolina": {"id": 324, "conference": "Sun Belt"},
}

def get_team_logo(team_name):
    """Get the ESPN logo URL for a team."""
    team = CFB_TEAMS.get(team_name)
    if team:
        return f"https://a.espncdn.com/i/teamlogos/ncaa/500/{team['id']}.png"
    return None

def get_team_info(team_name):
    """Get team info including logo URL."""
    team = CFB_TEAMS.get(team_name)
    if team:
        return {
            "name": team_name,
            "logo": f"https://a.espncdn.com/i/teamlogos/ncaa/500/{team['id']}.png",
            "conference": team["conference"]
        }
    return None

def find_team(search_term):
    """Find a team by partial name match (case insensitive)."""
    search_lower = search_term.lower()
    matches = []
    for team_name in CFB_TEAMS.keys():
        if search_lower in team_name.lower():
            matches.append(team_name)
    return matches

def get_all_teams():
    """Get list of all team names."""
    return sorted(CFB_TEAMS.keys())
