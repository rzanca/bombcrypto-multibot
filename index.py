# -*- coding: utf-8 -*-    
from bot import Bot

def start_bot():
    bot = Bot()
    try:
        bot.start()
    except:
        try:
            if bot is not None and bot.telegram is not None:
                bot.telegram.telsendtext('Ocorreu um erro no bot. Bot sendo reiniciado!')
            start_bot()
        except:
            start_bot()

if __name__ == '__main__':
    start_bot()
