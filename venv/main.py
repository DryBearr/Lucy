from discord_bot.bot import start_bot
import threading

if __name__ == '__main__':
    bot_thread = start_bot().join() # start the bot :3