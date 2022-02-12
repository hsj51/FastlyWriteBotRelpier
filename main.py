from pyrogram import Client, filters

from PIL import Image
import pytesseract

from dotenv import load_dotenv
from os import environ, remove
from time import time

try:
    CONFIG_ENV_URL = environ['CONFIG_ENV_URL']
    if len(CONFIG_ENV_URL) == 0:
        CONFIG_ENV_URL = None
    else:
        res = requests.get(CONFIG_ENV_URL)
        if res.status_code == 200:
            with open('config.env', 'wb+') as f:
                f.write(res.content)
                f.close()
        else:
            print(f"Failed to load config.env file [{res.status_code}]")
            raise KeyError
except KeyError:
    pass

load_dotenv('config.env')

try:
    SESSION_STRING = environ['SESSION_STRING']
    TELEGRAM_API = int(environ['TELEGRAM_API'])
    TELEGRAM_HASH = environ['TELEGRAM_HASH']
    BOT_USERNAMES =  environ['BOT_USERNAMES']
    CHAT_IDS =  environ['CHAT_IDS']
except KeyError:
    print("One or more env variables are missing or incorrect")
    exit(1)

if BOT_USERNAMES != '':
    BOT_USERNAMES = list(map(lambda x: int(x.strip()) if x.strip()[1:].isnumeric() else x.strip(), BOT_USERNAMES.strip().split(',')))
else:
    BOT_USERNAMES = ['FastlyWriteClone2Bot', 'FastlyWriteBot']

if CHAT_IDS != '':
    CHAT_IDS = list(map(lambda x:int(x.strip()) if x.strip()[1:].isnumeric() else x.strip(), CHAT_IDS.strip().split(',')))
else:
    CHAT_IDS = None

app = Client(SESSION_STRING, api_id=int(TELEGRAM_API), api_hash=TELEGRAM_HASH)

if SESSION_STRING == '':
    with Client(SESSION_STRING, api_id=TELEGRAM_API, api_hash=TELEGRAM_HASH) as client:
        print(f'\nSave this SESSION_STRING for futher use\n{client.export_session_string()}\n')

@app.on_message(filters.photo & filters.user(BOT_USERNAMES) & ( filters.group if CHAT_IDS == None else filters.chat(CHAT_IDS) ))
async def ocr(client, message):
    st = time()
    path = await client.download_media(message.photo)
    with Image.open(path).crop(( 150, 270, 1050, 370 )) as img:
        txt = pytesseract.image_to_string(img, config='--psm 8 --oem 1')
    await message.reply(txt.replace('~','').replace('-','').strip())
    print(f'{round(time() - st, 2)}s\t {txt}')
    remove(path)

app.run()
