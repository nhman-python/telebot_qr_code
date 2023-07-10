import logging
import os
import uuid
import argparse
import dotenv
import qrcode
import telebot

dotenv.load_dotenv('.env')


def default_path():
    current_directory = os.path.dirname(os.path.realpath(__file__))
    photo_folder_path = os.path.join(current_directory, 'photo')
    if not os.path.exists(photo_folder_path):
        os.mkdir(photo_folder_path)
    return photo_folder_path


logging.basicConfig(level=logging.INFO, filename='qrcode_logs.log', format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%d/%m/%Y %H:%M:%S")

def increment_stat():
    file_log = 'stat.log'
    try:
        with open(file_log, 'r+') as statistic:
            update_number = str(int(statistic.read()) + 1)
            statistic.seek(0)
            statistic.write(update_number)
            statistic.truncate()
            return update_number
    except FileNotFoundError:
        with open(file_log, 'w') as new:
            new.write('1')
            return '1'


def qr_create(text):
    try:
        path_file = os.path.join(default_path(), str(uuid.uuid4()) + ".png")
        img = qrcode.make(text)
        logging.info(f'new qr data {text}')
        img.save(path_file)
        return path_file
    except PermissionError as qr_e:
        logging.debug(f'Failed to create qr photo {qr_e}')
        return False


token = os.getenv('TOKEN')
app = telebot.TeleBot(token)


@app.message_handler(commands=['start', 'help'])
def commands_reply(message):
    if message.text == '/start':
        app.reply_to(message, 'בוט זה ייצור לך קוד qr אנא שלח קישור או טקסט')
    elif message.text == '/help':
        app.reply_to(message, 'שלח טקסט פשוט\nדוגמא https://google.com')
    else:
        app.reply_to(message, 'command not found please sent text and i reply with qr')


@app.message_handler(content_types=['text'])
def create_qr_image(message):
    text = message.text
    if not text or len(text) > 255:
        app.reply_to(message, 'נא להקליד טקסט תקין ולא יותר מ255 תווים')
        logging.warning(f'big or short text from @{message.chat.username}')
        return
    else:
        path = qr_create(text)
        with open(path, 'rb') as img:
            try:
                app.send_photo(message.chat.id, img)
                increment_stat()
                logging.info(f'qr photo sent to {message.chat.id}')
            except telebot.apihelper.ApiException as error1:
                app.reply_to(message, f'Failed to send photo {error1}')
                logging.debug(f'error create photo Failed {message.text} from {message.chat.username} error {error1}')

parser = argparse.ArgumentParser("telegram bot", description="this will run the bot qr telegram")

parser.add_argument("run", type=str)

args = parser.parse_args()


if __name__ == "__main__":
    if args.run == "run":
        logging.warning('start qr bot!')
        print('bot is up!')
        app.polling()
