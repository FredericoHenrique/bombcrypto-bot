import requests

def telegram_bot_sendtext(bot_message):
    bot_token = '5004237424:AAGTflh1M_cRKwubi3aNi5L1-i4Ncqg_TbQ'
    bot_chatID = '1326805236'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()
