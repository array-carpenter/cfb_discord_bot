import os
import json
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
from cfb_teams import get_team_info, find_team, get_all_teams

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
READY_CHANNEL_ID = int(os.getenv('READY_CHANNEL_ID', 0))
PLAYER_COUNT = int(os.getenv('PLAYER_COUNT', 4))

# File to store team registrations
TEAMS_FILE = 'registered_teams.json'

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


@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')


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

    # Save registration
    teams = load_teams()
    teams[str(user.id)] = team_info['name']
    save_teams(teams)

    # Create embed with team logo
    embed = discord.Embed(
        title="Team Registered!",
        description=f"**{user.display_name}** is now the **{team_info['name']}**!",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=team_info['logo'])
    embed.add_field(name="Conference", value=team_info['conference'], inline=True)

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


# Run the bot
if __name__ == '__main__':
    if not TOKEN:
        print("ERROR: No Discord token found. Create a .env file with DISCORD_TOKEN=your_token")
    else:
        bot.run(TOKEN)
