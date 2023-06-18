import os
import qrcode
import telebot
import uuid
import dotenv

dotenv.load_dotenv('.env')

default_path = os.path.dirname(os.path.abspath(__file__))


def qr_create(data):
    path_file = os.path.join(default_path, str(uuid.uuid4()) + ".png")
    img = qrcode.make(data)
    img.save(path_file)
    return path_file


token = os.getenv('TOKEN')
app = telebot.TeleBot(token)


@app.message_handler(commands=['start', 'help'])
def commands_reply(message):
    if message.text == '/start':
        app.reply_to(message, 'בוט זה ייצור לך קוד qr אנא שלח קישור או טקסט')
    elif message.text == '/help':
        app.reply_to(message, 'שלח טקסט פשוט\nדוגמא https://google.com')


@app.message_handler(content_types=['text'])
def create_qr_image(message):
    text = message.text
    if not text or len(text) > 255:
        app.reply_to(message, 'נא להקליד טקסט תקין ולא יותר מ255 תווים')
        return
    else:
        path = qr_create(text)
        with open(path, 'rb') as img:
            try:
                app.send_photo(message.chat.id, img)
            except telebot.apihelper.ApiException:
                app.reply_to(message, 'Failed to send photo')


app.polling()
