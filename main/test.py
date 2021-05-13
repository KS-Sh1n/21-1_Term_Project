import telegram

# Telegram Bot Configuration
bot = telegram.Bot(token = '1422791065:AAH_txqti5v5CbuRNTtgU-OEw7eTvpkmUfw')
chat_id = 1327186896

bot_text = '<b>{0}</b>\n  {1}\n\n<b>{2}</b>\n\n <a href = "{3}">Link</a>'.format(
    1, 2, 3, 4)

# Send real-time notification
bot.send_message(
    chat_id = chat_id, 
    text= "12312")