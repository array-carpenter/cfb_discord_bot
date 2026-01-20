import os
import json
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
from cfb_teams import get_team_info, find_team, get_all_teams
from history import (
    save_game, save_season, get_standings, get_head_to_head,
    get_team_history, get_championships, get_all_seasons
)

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
READY_CHANNEL_ID = int(os.getenv('READY_CHANNEL_ID', 0))
PLAYER_COUNT = int(os.getenv('PLAYER_COUNT', 4))

# File to store team registrations
TEAMS_FILE = 'registered_teams.json'
COACHING_HISTORY_FILE = 'coaching_history.json'

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Track who's ready
ready_players = set()


def load_teams():
    """Load registered teams from JSON file."""
    if os.path.exists(TEAMS_FILE):
        with open(TEAMS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_teams(teams):
    """Save registered teams to JSON file."""
    with open(TEAMS_FILE, 'w') as f:
        json.dump(teams, f, indent=2)


def get_user_team(user_id):
    """Get a user's registered team info."""
    teams = load_teams()
    team_name = teams.get(str(user_id))
    if team_name:
        return get_team_info(team_name)
    return None


def load_coaching_history():
    """Load coaching history from JSON file."""
    if os.path.exists(COACHING_HISTORY_FILE):
        with open(COACHING_HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []


def save_coaching_history(history):
    """Save coaching history to JSON file."""
    with open(COACHING_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def log_coaching_change(user_id, user_name, old_team, new_team):
    """Log a coaching change."""
    history = load_coaching_history()
    history.append({
        'user_id': str(user_id),
        'user_name': user_name,
        'old_team': old_team,
        'new_team': new_team,
        'date': datetime.now().isoformat()
    })
    save_coaching_history(history)


@bot.event
async def on_ready():
    print(f'{bot.user} is online!', flush=True)
    try:
        # Sync to guild first (instant for your server)
        guild = discord.Object(id=671891039765790731)
        guild_synced = await bot.tree.sync(guild=guild)
        print(f'Synced {len(guild_synced)} command(s) to guild', flush=True)

        # Also sync globally (for other servers/devices, takes up to 1 hour)
        global_synced = await bot.tree.sync()
        print(f'Synced {len(global_synced)} global command(s)', flush=True)
    except Exception as e:
        print(f'Failed to sync commands: {e}', flush=True)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f'Command error: {error}')
    try:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
    except:
        pass


# Autocomplete for team names
async def team_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    try:
        teams = get_all_teams()
        if current:
            matches = [t for t in teams if current.lower() in t.lower()][:25]
        else:
            matches = teams[:25]
        return [app_commands.Choice(name=team, value=team) for team in matches]
    except Exception as e:
        print(f"Autocomplete error: {e}")
        return []


@bot.tree.command(name='register', description='Register your CFB team')
@app_commands.describe(team='The team name (e.g., Georgia, Ohio State, Alabama)')
@app_commands.autocomplete(team=team_autocomplete)
async def register(interaction: discord.Interaction, team: str):
    user = interaction.user
    team_info = get_team_info(team)

    if not team_info:
        # Try to find partial matches
        matches = find_team(team)
        if matches:
            match_list = ", ".join(matches[:10])
            await interaction.response.send_message(
                f"Team '{team}' not found. Did you mean: {match_list}?",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Team '{team}' not found. Use `/teamlist` to see available teams.",
                ephemeral=True
            )
        return

    # Check for coaching change
    teams = load_teams()
    old_team = teams.get(str(user.id))
    is_coaching_change = old_team and old_team != team_info['name']

    # Log coaching change if switching teams
    if is_coaching_change:
        log_coaching_change(user.id, user.display_name, old_team, team_info['name'])

    # Save registration
    teams[str(user.id)] = team_info['name']
    save_teams(teams)

    # Create embed with team logo
    if is_coaching_change:
        embed = discord.Embed(
            title="Coaching Change!",
            description=f"**{user.display_name}** has left **{old_team}** to become the new head coach at **{team_info['name']}**!",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Previous Team", value=old_team, inline=True)
        embed.add_field(name="New Team", value=team_info['name'], inline=True)
    else:
        embed = discord.Embed(
            title="Team Registered!",
            description=f"**{user.display_name}** is now the **{team_info['name']}**!",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Conference", value=team_info['conference'], inline=True)

    embed.set_thumbnail(url=team_info['logo'])

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='teams', description='See all registered teams')
async def teams(interaction: discord.Interaction):
    registered = load_teams()

    embed = discord.Embed(
        title="Registered Teams",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    if not registered:
        embed.description = "No teams registered yet. Use `/register` to claim your team!"
    else:
        team_list = []
        for user_id, team_name in registered.items():
            team_info = get_team_info(team_name)
            try:
                member = await interaction.guild.fetch_member(int(user_id))
                display_name = member.display_name
            except:
                display_name = f"<@{user_id}>"

            conf = team_info['conference'] if team_info else "Unknown"
            team_list.append(f"**{display_name}**: {team_name} ({conf})")

        embed.description = "\n".join(team_list)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='teamlist', description='List all available CFB teams')
async def teamlist(interaction: discord.Interaction):
    teams = get_all_teams()

    # Split into chunks for Discord's character limit
    chunk_size = 50
    team_chunks = [teams[i:i + chunk_size] for i in range(0, len(teams), chunk_size)]

    embed = discord.Embed(
        title="Available CFB Teams",
        description=f"**{len(teams)} teams available.** Use `/register [team]` to claim yours.",
        color=discord.Color.blue()
    )

    # Just show first chunk in embed, mention there are more
    embed.add_field(
        name="Teams (A-M)",
        value=", ".join([t for t in teams if t[0].upper() <= 'M'][:40]),
        inline=False
    )
    embed.add_field(
        name="Teams (N-Z)",
        value=", ".join([t for t in teams if t[0].upper() > 'M'][:40]),
        inline=False
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='ready', description='Mark yourself as ready to advance')
async def ready(interaction: discord.Interaction):
    user = interaction.user

    if user.id in ready_players:
        await interaction.response.send_message(
            f"You're already marked as ready, {user.display_name}!",
            ephemeral=True
        )
        return

    ready_players.add(user.id)
    count = len(ready_players)

    # Get user's team info
    team_info = get_user_team(user.id)

    # Create embed
    if team_info:
        embed = discord.Embed(
            title="Ready to Advance",
            description=f"**{team_info['name']}** ({user.display_name}) is ready to advance!",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=team_info['logo'])
    else:
        embed = discord.Embed(
            title="Ready to Advance",
            description=f"**{user.display_name}** is ready to advance!",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )

    embed.add_field(name="Ready Count", value=f"{count}/{PLAYER_COUNT}", inline=False)

    await interaction.response.send_message(embed=embed)

    # Check if everyone is ready
    if count >= PLAYER_COUNT:
        channel = bot.get_channel(READY_CHANNEL_ID) or interaction.channel

        all_ready_embed = discord.Embed(
            title="Everyone is Ready!",
            description="All players are ready to advance! Time to move to the next week!",
            color=discord.Color.gold()
        )
        await channel.send("@here", embed=all_ready_embed)


@bot.tree.command(name='unready', description='Remove yourself from the ready list')
async def unready(interaction: discord.Interaction):
    user = interaction.user

    if user.id not in ready_players:
        await interaction.response.send_message(
            f"You weren't marked as ready, {user.display_name}.",
            ephemeral=True
        )
        return

    ready_players.discard(user.id)
    count = len(ready_players)

    # Get user's team info
    team_info = get_user_team(user.id)

    if team_info:
        embed = discord.Embed(
            title="No Longer Ready",
            description=f"**{team_info['name']}** ({user.display_name}) is no longer ready.",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=team_info['logo'])
    else:
        embed = discord.Embed(
            title="No Longer Ready",
            description=f"**{user.display_name}** is no longer ready.",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )

    embed.add_field(name="Ready Count", value=f"{count}/{PLAYER_COUNT}", inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='status', description='Check who is ready to advance')
async def status(interaction: discord.Interaction):
    count = len(ready_players)

    embed = discord.Embed(
        title="Ready Status",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    embed.add_field(name="Ready Count", value=f"{count}/{PLAYER_COUNT}", inline=False)

    if ready_players:
        ready_list = []
        for player_id in ready_players:
            team_info = get_user_team(player_id)
            try:
                member = await interaction.guild.fetch_member(player_id)
                display_name = member.display_name
            except:
                display_name = f"<@{player_id}>"

            if team_info:
                ready_list.append(f"✅ **{team_info['name']}** ({display_name})")
            else:
                ready_list.append(f"✅ {display_name}")

        embed.add_field(name="Ready Players", value="\n".join(ready_list), inline=False)
    else:
        embed.add_field(name="Ready Players", value="No one is ready yet.", inline=False)

    # Show who's NOT ready
    registered = load_teams()
    not_ready = []
    for user_id, team_name in registered.items():
        if int(user_id) not in ready_players:
            try:
                member = await interaction.guild.fetch_member(int(user_id))
                display_name = member.display_name
            except:
                display_name = f"<@{user_id}>"
            not_ready.append(f"⏳ **{team_name}** ({display_name})")

    if not_ready:
        embed.add_field(name="Waiting On", value="\n".join(not_ready), inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='advance', description='Clear all ready status (use after advancing)')
async def advance(interaction: discord.Interaction):
    count = len(ready_players)
    ready_players.clear()

    embed = discord.Embed(
        title="Week Advanced!",
        description=f"Ready list cleared. {count} player(s) were marked ready.\n\nUse `/ready` when you're ready for the next advance!",
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='coachinghistory', description='View coaching changes/carousel')
async def coachinghistory(interaction: discord.Interaction):
    history = load_coaching_history()

    if not history:
        await interaction.response.send_message("No coaching changes recorded yet!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🔄 Coaching Carousel",
        description="History of coaching changes",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )

    # Show most recent changes first
    for change in reversed(history[-10:]):
        date = change['date'][:10]  # Just the date part
        embed.add_field(
            name=f"{change['user_name']} ({date})",
            value=f"{change['old_team']} → {change['new_team']}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


# ============ HISTORY COMMANDS ============

@bot.tree.command(name='loggame', description='Log a game result')
@app_commands.describe(
    season='Season year (e.g., 2024)',
    week='Week number',
    team1='First team',
    score1='First team score',
    team2='Second team',
    score2='Second team score'
)
@app_commands.autocomplete(team1=team_autocomplete, team2=team_autocomplete)
async def loggame(interaction: discord.Interaction, season: int, week: int,
                  team1: str, score1: int, team2: str, score2: int):
    save_game(season, week, team1, team2, score1, score2)

    winner = team1 if score1 > score2 else team2
    winner_info = get_team_info(winner)

    embed = discord.Embed(
        title="Game Logged!",
        description=f"**{team1}** {score1} - {score2} **{team2}**",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    embed.add_field(name="Season", value=season, inline=True)
    embed.add_field(name="Week", value=week, inline=True)
    embed.add_field(name="Winner", value=winner, inline=True)

    if winner_info:
        embed.set_thumbnail(url=winner_info['logo'])

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='standings', description='View standings')
@app_commands.describe(season='Season year (leave empty for all-time)')
async def standings(interaction: discord.Interaction, season: int = None):
    records = get_standings(season)

    if not records:
        await interaction.response.send_message("No games logged yet!", ephemeral=True)
        return

    title = f"{season} Standings" if season else "All-Time Standings"
    embed = discord.Embed(title=title, color=discord.Color.blue(), timestamp=datetime.now())

    standings_text = []
    for i, (team, record) in enumerate(records[:15], 1):
        pf, pa = record['points_for'], record['points_against']
        diff = pf - pa
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        standings_text.append(
            f"**{i}. {team}** ({record['wins']}-{record['losses']}) | PF: {pf} | PA: {pa} | {diff_str}"
        )

    embed.description = "\n".join(standings_text)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='h2h', description='Head-to-head record between two teams')
@app_commands.describe(team1='First team', team2='Second team')
@app_commands.autocomplete(team1=team_autocomplete, team2=team_autocomplete)
async def h2h(interaction: discord.Interaction, team1: str, team2: str):
    results = get_head_to_head(team1, team2)

    if not results['games']:
        await interaction.response.send_message(
            f"No games found between {team1} and {team2}.", ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"{team1} vs {team2}",
        description=f"**{team1}** leads **{results['team1_wins']}-{results['team2_wins']}**"
        if results['team1_wins'] != results['team2_wins']
        else f"Series tied **{results['team1_wins']}-{results['team2_wins']}**",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    # Show recent games
    games_text = []
    for game in results['games'][-5:]:  # Last 5 games
        games_text.append(
            f"S{game['season']} W{game['week']}: {game['team1']} {game['score1']} - {game['score2']} {game['team2']}"
        )

    if games_text:
        embed.add_field(name="Recent Games", value="\n".join(games_text), inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='teamhistory', description='View a team\'s game history')
@app_commands.describe(team='Team name')
@app_commands.autocomplete(team=team_autocomplete)
async def teamhistory(interaction: discord.Interaction, team: str):
    games = get_team_history(team)
    team_info = get_team_info(team)

    if not games:
        await interaction.response.send_message(f"No games found for {team}.", ephemeral=True)
        return

    wins = sum(1 for g in games if g['result'] == 'W')
    losses = len(games) - wins

    embed = discord.Embed(
        title=f"{team} History",
        description=f"**Record: {wins}-{losses}**",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    if team_info:
        embed.set_thumbnail(url=team_info['logo'])

    # Show recent games
    games_text = []
    for game in games[-10:]:  # Last 10 games
        emoji = "✅" if game['result'] == 'W' else "❌"
        games_text.append(f"{emoji} S{game['season']} W{game['week']}: vs {game['opponent']} ({game['score']})")

    embed.add_field(name="Recent Games", value="\n".join(games_text), inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='logseason', description='Log a season championship')
@app_commands.describe(
    season='Season year',
    champion='National Champion',
    runner_up='Runner-up team',
    heisman='Heisman winner name',
    heisman_team='Heisman winner team'
)
@app_commands.autocomplete(champion=team_autocomplete, runner_up=team_autocomplete, heisman_team=team_autocomplete)
async def logseason(interaction: discord.Interaction, season: int, champion: str,
                    runner_up: str, heisman: str, heisman_team: str):
    save_season(season, champion, runner_up, heisman, heisman_team)

    champ_info = get_team_info(champion)

    embed = discord.Embed(
        title=f"{season} Season Recorded!",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    embed.add_field(name="🏆 National Champion", value=champion, inline=False)
    embed.add_field(name="🥈 Runner-Up", value=runner_up, inline=False)
    embed.add_field(name="🏅 Heisman Trophy", value=f"{heisman} ({heisman_team})", inline=False)

    if champ_info:
        embed.set_thumbnail(url=champ_info['logo'])

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='champions', description='View championship history')
async def champions(interaction: discord.Interaction):
    history = get_championships()

    if not history:
        await interaction.response.send_message("No championship history logged yet!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🏆 Championship History",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )

    for season in history[:10]:  # Last 10 seasons
        embed.add_field(
            name=f"{season['season']} Season",
            value=f"**Champion:** {season['champion']}\n**Runner-Up:** {season['runner_up']}\n**Heisman:** {season['heisman']} ({season['heisman_team']})",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


# Run the bot
if __name__ == '__main__':
    if not TOKEN:
        print("ERROR: No Discord token found. Create a .env file with DISCORD_TOKEN=your_token")
    else:
        bot.run(TOKEN)
