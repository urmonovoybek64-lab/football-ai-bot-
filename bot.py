
import os
import requests
import telebot

TOKEN = os.getenv("BOT_TOKEN")
ODDS_KEY = os.getenv("ODDS_API_KEY")

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi")

bot = telebot.TeleBot(TOKEN)

LEAGUES = [
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one"
]

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "Assalomu alaykum! ⚽ Football AI botga xush kelibsiz!\n\n"
        "Men futbol o'yinlarini tahlil qilaman.\n"
        "/today - Bugungi tahlillar"
    )

@bot.message_handler(commands=["today"])
def today(message):
    if not ODDS_KEY:
        bot.reply_to(message, "API kaliti hali ulanmagan.")
        return

    msg = bot.reply_to(message, "⚽ O'yinlar tahlil qilinmoqda...")

    picks = []

    for league in LEAGUES:
        url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/"
        params = {
            "apiKey": ODDS_KEY,
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal"
        }

        try:
            data = requests.get(url, params=params, timeout=20).json()

            if not isinstance(data, list):
                continue

            for game in data:
                best = {}

                for bookmaker in game.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        if market.get("key") != "h2h":
                            continue

                        for outcome in market.get("outcomes", []):
                            name = outcome["name"]
                            price = float(outcome["price"])

                            if name not in best or price < best[name]:
                                best[name] = price

                if not best:
                    continue

                # Eng yuqori taxminiy ehtimolli natija
                name, odds = min(best.items(), key=lambda x: x[1])

                if 1.35 <= odds <= 2.50:
                    picks.append({
                        "match": game["home_team"] + " - " + game["away_team"],
                        "pick": name,
                        "odds": odds
                    })

        except Exception:
            continue

    picks.sort(key=lambda x: x["odds"])

    selected = []
    total = 1.0

    for pick in picks:
        if len(selected) >= 10:
            break
        if total * pick["odds"] <= 100:
            selected.append(pick)
            total *= pick["odds"]

    if len(selected) < 10 or total < 40:
        bot.edit_message_text(
            "Bugun 50 koeffitsiyentga yaqin 10 ta mos o'yin topilmadi. "
            "Majburan taxmin bermayman.",
            message.chat.id,
            msg.message_id
        )
        return

    result = "⚽ FOOTBALL AI TAHLILI\n\n"

    for i, p in enumerate(selected, 1):
        result += (
            f"{i}. {p['match']}\n"
            f"Tanlov: {p['pick']}\n"
            f"Koeffitsiyent: {p['odds']}\n\n"
        )

    result += f"🔥 Jami koeffitsiyent: {total:.2f}\n"
    result += "\nBu taxminlar kafolat emas. Pul tikish xavfli."

    bot.edit_message_text(result, message.chat.id, msg.message_id)

bot.infinity_polling()
                        
