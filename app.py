import os
import json
import logging
import random
from datetime import time
import pytz
from google import genai

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, JobQueue
)
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE")

client = genai.Client(api_key=GEMINI_API_KEY)

USERS_FILE = "users.json"
GLOBAL_FILE = "global.json"  # stores shared sign history

# --- CONFIG ---
ADMIN_ID = "2022211370"
SIGN_WHITELIST = {"2022211370"}  # user IDs allowed to use /sign
DONATION_CARD = "4441 1110 2380 7435"
DONATION_CHANCE = 0.15  # 15% chance each scheduled send includes a donation nudge

SEND_TIMES = [
    time(7, 0, tzinfo=pytz.timezone("Europe/Kiev")),
    time(11, 0, tzinfo=pytz.timezone("Europe/Kiev")),
    time(14, 30, tzinfo=pytz.timezone("Europe/Kiev")),
    time(17, 0, tzinfo=pytz.timezone("Europe/Kiev")),
    time(21, 0, tzinfo=pytz.timezone("Europe/Kiev")),
]

EXAMPLES = """
- he's literally scared to admit it
- you've been friendzoning him and you know it
- someone from your past misses you (no it's not him)
- your vibe today is unmatched and that's not up for debate
- stop checking his profile, you're better than this
- buy yourself snacks, you've earned it
- the stars are honestly shocked by your behavior rn
- give him 3 days. if he doesn't text — let it go
- you radiate main character energy and everyone sees it
- that wasn't a coincidence, just saying
- your next situationship is closer than you think
- spoiler: it's mutual. he's just a coward
- today will end in tears but like, the fun kind
- someone in your friend group is lowkey obsessed with you
- you need to stop, but you won't, and honestly same
- the audacity you have today is actually kind of impressive
- get some sleep. your bad decisions can wait till tomorrow
- you're not over it and that's okay. but also get over it
"""

DONATION_MESSAGES = [
    f"p.s. if the signs have been hitting lately, you can buy me a coffee ☕ — {DONATION_CARD} (monobank)",
    f"p.s. keeping this running costs time and love 🫶 card: {DONATION_CARD} (monobank), any amount appreciated",
    f"p.s. if you feel like it — {DONATION_CARD} monobank 💛 no pressure at all",
    f"p.s. this bot runs on vibes and occasionally money 😅 {DONATION_CARD} (monobank)",
]


# --- STORAGE ---

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def load_global() -> dict:
    if os.path.exists(GLOBAL_FILE):
        with open(GLOBAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"used": []}


def save_global(data: dict):
    with open(GLOBAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --- SIGN GENERATION ---

def generate_sign(used_signs: list) -> str:
    used_block = ""
    if used_signs:
        recent = used_signs[-60:]
        used_block = "\n\nALREADY USED SIGNS (do not repeat or make anything similar):\n" + "\n".join(f"- {s}" for s in recent)

    prompt = f"""You write daily "signs" for a girl — short, punchy, funny or oddly specific little predictions/observations in a very casual, human tone. Think: a chaotic bestie who somehow knows everything about your life.

Style examples (learn the vibe, don't copy):
{EXAMPLES}{used_block}

Write ONE new sign. Rules:
- 5 to 20 words
- lowercase throughout, no punctuation at the end
- sounds like a real person texting, not an AI or a horoscope app
- mix of: relationships, crushes, daily life, food, sleep, self-esteem, laziness, drama, random observations
- sometimes specific and absurd, sometimes uncomfortably accurate
- no hashtags, no quotes, no formatting, no em dashes
- DO NOT start with "you" more than half the time, vary the structure
- DO NOT mention strangers  
- Signs HAVE to be meaningfull

Reply with ONLY the sign text, nothing else."""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    sign = response.text.strip().strip('"').strip("'")
    return sign


def get_shared_sign() -> str:
    """Generate one sign for everyone in the current broadcast."""
    data = load_global()
    sign = generate_sign(data["used"])
    data["used"].append(sign)
    if len(data["used"]) > 500:
        data["used"] = data["used"][-500:]
    save_global(data)
    return sign


def get_personal_sign(user_id: str, users: dict) -> str:
    """Generate a personal sign for /sign command (per-user history)."""
    global_data = load_global()
    user = users.setdefault(user_id, {"used": [], "name": "babe", "no_donation": False})
    sign = generate_sign(global_data["used"] + user["used"])
    user["used"].append(sign)
    global_data["used"].append(sign)
    if len(user["used"]) > 200:
        user["used"] = user["used"][-200:]
    if len(global_data["used"]) > 500:
        global_data["used"] = global_data["used"][-500:]
    save_users(users)
    save_global(global_data)
    return sign


# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    name = update.effective_user.first_name or "babe"
    users = load_users()
    if user_id not in users:
        users[user_id] = {"used": [], "name": name, "no_donation": False}
        save_users(users)
        await update.message.reply_text(
            f"hey {name} 🌙\n\n"
            "you're gonna get signs a few times a day — morning, afternoon, evening.\n\n"
            "type /sign if you want one right now ✨"
        )
    else:
        users[user_id]["name"] = name
        save_users(users)
        await update.message.reply_text(
            f"you're already in {name} 😌\n/sign to get a sign right now"
        )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    if user_id in users:
        del users[user_id]
        save_users(users)
    await update.message.reply_text("ok, no more signs 🌑\nchange your mind? /start")


async def sign_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in SIGN_WHITELIST:
        await update.message.reply_text("this one's not for everyone 🌙")
        return

    users = load_users()
    if user_id not in users:
        await update.message.reply_text("type /start first 💫")
        return

    await update.message.reply_text("...")

    try:
        sign = get_personal_sign(user_id, users)
        await update.message.reply_text(sign)
    except Exception as e:
        logger.error(f"Failed to generate sign: {e}")
        await update.message.reply_text("signs are quiet today 🌫 try again later")


async def checkschedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID:
        return
    jobs = context.application.job_queue.jobs()
    if not jobs:
        await update.message.reply_text("no active jobs — scheduler is not running!")
        return
    lines = ["scheduled jobs:\n"]
    for job in jobs:
        next_run = job.next_t.strftime("%H:%M:%S %d.%m.%Y") if job.next_t else "unknown"
        lines.append(f"next run: {next_run} (UTC)")
    await update.message.reply_text("\n".join(lines))


async def nodonation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command: /nodonation <user_id> — disable donation nudges for a user."""
    if str(update.effective_user.id) != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("usage: /nodonation <user_id>")
        return
    target_id = context.args[0]
    users = load_users()
    if target_id not in users:
        await update.message.reply_text(f"user {target_id} not found")
        return
    users[target_id]["no_donation"] = True
    save_users(users)
    await update.message.reply_text(f"done, {target_id} won't see donation messages")


async def whitelist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command: /whitelist <user_id> — add user to /sign whitelist."""
    if str(update.effective_user.id) != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("usage: /whitelist <user_id>")
        return
    target_id = context.args[0]
    SIGN_WHITELIST.add(target_id)
    await update.message.reply_text(f"done, {target_id} can now use /sign")


async def send_scheduled_signs(context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    if not users:
        return

    try:
        sign = get_shared_sign()
    except Exception as e:
        logger.error(f"Failed to generate shared sign: {e}")
        return

    include_donation = random.random() < DONATION_CHANCE
    donation_msg = random.choice(DONATION_MESSAGES) if include_donation else None

    for user_id, data in list(users.items()):
        try:
            text = f"{sign}"
            if donation_msg and not data.get("no_donation", False):
                text += f"\n\n{donation_msg}"
            await context.bot.send_message(chat_id=int(user_id), text=text)
        except Exception as e:
            logger.warning(f"Failed to send to {user_id}: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("sign", sign_command))
    app.add_handler(CommandHandler("checkschedule", checkschedule_command))
    app.add_handler(CommandHandler("nodonation", nodonation_command))
    app.add_handler(CommandHandler("whitelist", whitelist_command))

    job_queue: JobQueue = app.job_queue
    for t in SEND_TIMES:
        job_queue.run_daily(send_scheduled_signs, time=t)

    logger.info("Bot started. Ready.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()