from discord_bot import bot, DISCORD_TOKEN
import threading

def start_bot():
    bot_thread = threading.Thread(target=bot.run, args=(DISCORD_TOKEN,))
    bot_thread.start()
    return bot_thread