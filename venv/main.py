from discord_bot.bot import start_bot
import threading

if __name__ == '__main__':
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    bot_thread.join()