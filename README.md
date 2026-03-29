# Telegram Horoscope Bot 🌙

A fully-automated Telegram bot that generates personalized daily horoscopes using Google's Gemini API. Delivers 5 curated signs throughout the day with intelligent scheduling and user management.

**[Add Bot to Telegram](https://t.me/veronika_tebe_znak_bot)** | **Status:** Live & Active

---

## Features

✨ **AI-Powered Sign Generation**
- Uses Google Gemini API to generate unique, personality-filled daily signs
- Casual, conversational tone — sounds like a chaotic best friend, not a generic app
- Intelligent deduplication to avoid repeating signs over time

⏰ **Intelligent Scheduling**
- Automatic daily broadcasts at 5 strategically timed intervals:
  - 7:00 AM, 11:00 AM, 2:30 PM, 5:00 PM, 9:00 PM (Europe/Kiev timezone)
- Per-user history tracking to prevent sign repetition
- Global sign history shared across all users to maintain variety

💳 **Monetization Support**
- Optional donation integration (15% chance per broadcast)
- Customizable donation messaging without being intrusive
- Admin control over per-user donation preferences

👤 **User Management**
- One-command subscription: `/start`
- Simple unsubscribe: `/stop`
- Per-user configuration and history tracking
- Admin whitelist system for restricted commands

---

## Tech Stack

- **Language:** Python 3.8+
- **Telegram:** `python-telegram-bot` (v21+)
- **AI:** Google Gemini API (`google-genai`)
- **Scheduling:** Python's built-in `APScheduler` (via telegram-bot's JobQueue)
- **Storage:** JSON-based user persistence
- **Timezone:** `pytz` for timezone-aware scheduling

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Google Gemini API Key (from [Google AI Studio](https://aistudio.google.com/))

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YourUsername/telegram-horoscope-bot.git
   cd telegram-horoscope-bot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

The bot will start polling for updates and schedule the daily sign broadcasts.

---

## Usage

### User Commands

| Command | Description |
|---------|-------------|
| `/start` | Subscribe to daily signs (5x per day) |
| `/stop` | Unsubscribe and remove your data |
| `/sign` | Get an instant sign (whitelist only) |

### Admin Commands

| Command | Description |
|---------|-------------|
| `/checkschedule` | View all active scheduled jobs |
| `/nodonation <user_id>` | Disable donation messages for a specific user |
| `/whitelist <user_id>` | Grant `/sign` command access to a user |

---

## How It Works

### Sign Generation Pipeline

1. **Prompt Engineering**: Each sign request sends a detailed prompt to Gemini API that includes:
   - Style guidelines (casual, conversational, human-like)
   - Examples of previous signs
   - History of recently-used signs (to avoid repetition)
   - Strict formatting rules (lowercase, no punctuation, 5-20 words)

2. **Deduplication**: 
   - Maintains a global pool of the last 500 generated signs
   - Per-user history of up to 200 signs
   - API rejects similar signs by design through prompt constraints

3. **Scheduled Broadcasting**:
   - JobQueue runs `send_scheduled_signs()` at each configured time
   - Generates a shared sign for all users
   - Sends with optional donation nudge (15% chance)
   - Respects per-user donation preferences

4. **Persistent Storage**:
   - `users.json`: Tracks subscriptions, preferences, and personal sign history
   - `global.json`: Maintains shared sign history for deduplication

---

## Project Structure

```
telegram-horoscope-bot/
├── bot.py                 # Main bot application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── users.json            # User subscriptions & preferences (auto-generated)
├── global.json           # Global sign history (auto-generated)
└── README.md             # This file
```

---

## Key Implementation Details

### Why This Approach?

- **Gemini API over other models**: Cost-effective, fast response times, excellent for creative content generation
- **JSON-based storage**: Simple, no external dependencies, works well for small-to-medium user bases
- **Per-user + global deduplication**: Balances personalization with variety across the user base
- **Scheduled broadcasting**: More reliable than interval-based scheduling for timezone consistency

### Challenges Solved

✅ **Sign Repetition**: Implemented dual-history system (global + per-user) with API-level constraints  
✅ **Timezone Consistency**: Used `pytz` with explicit timezone configuration for reliable daily broadcasts  
✅ **API Failures**: Added try-catch blocks with graceful fallbacks and logging  
✅ **Scale**: JSON storage automatically prunes old signs to maintain performance  

---

## Configuration

Edit the constants at the top of `bot.py` to customize:

```python
SEND_TIMES = [
    time(7, 0, tzinfo=pytz.timezone("Europe/Kiev")),
    # ... add or modify times here
]

DONATION_CHANCE = 0.15  # 15% chance of donation message
DONATION_CARD = "your_card_number"  # Or any payment method
ADMIN_ID = "your_telegram_id"
```

---

## Deployment

This bot is designed to run 24/7. Recommended hosting:

- **VPS**: DigitalOcean, Linode, Hetzner (cheapest option)
- **Serverless**: AWS Lambda with custom scheduling (more complex setup)
- **Shared Hosting**: Any provider with Python support

### Running as a Background Service (Linux)

Use `systemd` or `supervisor` to keep the bot running:

```bash
# Create systemd service file
sudo nano /etc/systemd/system/telegram-bot.service
```

```ini
[Unit]
Description=Telegram Horoscope Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bot
ExecStart=/path/to/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

---

## Credits & Attribution

- **Telegram Bot API**: Official [Telegram Bot API](https://core.telegram.org/bots)
- **python-telegram-bot**: [Library](https://github.com/python-telegram-bot/python-telegram-bot) for Telegram integration
- **Google Gemini API**: [Gemini API](https://ai.google.dev/) for AI-powered content generation

---

## License

This project is open source and available under the MIT License.

---

## Future Improvements

- [ ] Database integration (PostgreSQL) for better scalability
- [ ] Multi-language support
- [ ] Web dashboard for user analytics
- [ ] Custom sign preferences per user (filter by topic)
- [ ] Integration with other messaging platforms (Discord, WhatsApp)

---

## Support & Contact

Found a bug? Have a suggestion?  
Feel free to open an issue or reach out directly on Telegram.

**Bot Link:** [@veronika_tebe_znak_bot](https://t.me/veronika_tebe_znak_bot)

---

**Made with ☕ and 🌙**
