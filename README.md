# CFB Dynasty Discord Bot

A simple Discord bot to coordinate "ready to advance" status for your College Football online dynasty league.

## Features

- `/ready` - Mark yourself as ready to advance to the next week
- `/unready` - Remove yourself from the ready list
- `/status` - See who's currently ready
- `/advance` - Clear the ready list after advancing (start fresh for next week)
- Auto-notification when all players are ready

## Setup

### 1. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under the bot's username, click "Reset Token" and copy your token (keep this secret!)
5. Enable "Server Members Intent" under Privileged Gateway Intents

### 2. Invite the Bot to Your Server

1. Go to the "OAuth2" > "URL Generator" tab
2. Select scopes: `bot` and `applications.commands`
3. Select bot permissions: `Send Messages`, `Use Slash Commands`, `Mention Everyone`
4. Copy the generated URL and open it in your browser
5. Select your server and authorize

### 3. Configure the Bot

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```
   DISCORD_TOKEN=your_bot_token_here
   READY_CHANNEL_ID=your_channel_id
   PLAYER_COUNT=4
   ```

   To get a channel ID: Enable Developer Mode in Discord settings, then right-click the channel > Copy ID

### 4. Install and Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

The bot should come online and sync its slash commands. First sync may take a few minutes to propagate.

## Usage

Once the bot is running in your server:

1. When you're done with your games for the week, type `/ready`
2. Check status anytime with `/status`
3. When everyone is ready, the bot will ping the channel
4. After advancing, use `/advance` to reset for the next week

## Hosting Options

To keep the bot running 24/7:

- **Your PC** - Just keep the script running (free but requires your PC to be on)
- **Raspberry Pi** - Low-power always-on option
- **Free cloud**: [Railway](https://railway.app), [Render](https://render.com), or [Fly.io](https://fly.io)
- **Paid cloud**: Any VPS provider (DigitalOcean, Linode, etc.)

## License

MIT - Use it however you want!
