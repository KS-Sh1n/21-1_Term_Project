import telegram

# Telegram Bot Configuration
bot = telegram.Bot(token = '1822963809:AAEKMWyn9uBHXQ_m6D4yctWLcmC9bpsU8us')
chat_id = 1327186896

a = bot.send_message(
    chat_id = chat_id, 
    text = "." * 40
    )
id = a.message_id
print(id)

'''
 b = bot.delete_message(
    chat_id = chat_id,
    message_id = 153,
)
print(b)
'''