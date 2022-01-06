import requests
import telegram

TELEGRAM_BOT_TOKEN = "5004237424:AAGTflh1M_cRKwubi3aNi5L1-i4Ncqg_TbQ"
TELEGRAM_CHAT_ID = "1326805236"

def telegram_bot_sendtext(bot_message, num_try=0):
    global bot
    try:
        return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=bot_message)
    except:
        if num_try == 1:
            bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
            return telegram_bot_sendtext(bot_message, 1)
        return 0


def telegram_bot_sendphoto(photo_path, num_try=0):
    global bot
    try:
        return bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=open(photo_path, "rb"))
    except:
        if num_try == 1:
            bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
            return telegram_bot_sendphoto(photo_path, 1)
        return 0