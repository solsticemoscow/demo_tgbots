import datetime
import os, shutil
import types

from random import randrange

import dropbox
from aiogram.utils import executor
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from module_dropbox import DropboxModule
import logging
import os
import re
import urllib
import time

from dotenv import load_dotenv
from youtubesearchpython import VideosSearch
import youtube_dl

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import *
from aiogram import *
from aiogram.dispatcher import *
from module_main_fuctions import *
from aiogram.dispatcher.filters.state import *
from aiogram.utils.exceptions import *

load_dotenv()


TELEGRAM_SOLBOT_TOKEN = os.getenv('TELEGRAM_SOLBOT_TOKEN')



m1 = MAIN_FUNC()
d1 = DropboxModule()

MUSIC_PHRASE = [
    'Music',
    'Audio'
]


REGEX_UT = "(?:.+?)?(?:\/v\/|watch\/|\?v=|\&v=|youtu\.be\/|\/v=|^youtu\.be\/)([a-zA-Z0-9_-]{11})+"

bot = Bot(TELEGRAM_SOLBOT_TOKEN)
STORAGE = MemoryStorage()
dp = Dispatcher(bot, storage=STORAGE)


############################ Keyboards reply ########################################

def keyboard_main():
    button1 = KeyboardButton('⚙ ACTION')
    button3 = KeyboardButton('🤖 CHATBOT')
    keyboard = ReplyKeyboardMarkup([[button1], [button3]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def keyboard_menu():
    button1 = KeyboardButton('📋 MyData')
    button2 = KeyboardButton('♻ Flush FILES')
    button_back = KeyboardButton('❌ Cancel')
    keyboard = ReplyKeyboardMarkup([[button1], [button2], [button_back]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def keyboard_add():
    button1 = KeyboardButton('✅ Yes')
    button2 = KeyboardButton('❌ No')
    button3 = KeyboardButton('💻 RebootMyPC')
    button_back = KeyboardButton('❌ Cancel')
    keyboard = ReplyKeyboardMarkup([[button1, button2], [button3], [button_back]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard


async def f_mydata(message: types.Message):
    await bot.send_message(
        message.chat.id,
        text=f'`alexander.tsyrkun@gmail.com`\n\n'
             f'`sanchez01@mail.ru`\n\n'
             f'`123qweASD!`\n\n'
             f'`solstice@solmusic.moscow`',
        parse_mode="Markdown",
        reply_markup=keyboard_menu())

async def f_yot_to_mp3(message: types.Message):
    url = message.text

    # async def my_hook(d):
    #     if d['status'] == 'downloading':
    #          await bot.edit_message_text(
    #             chat_id=message.chat.id,
    #             message_id=MSG,
    #             text=f'*Progress*:_{d["_percent_str"]}_ with speed: _{d["_speed_str"]}_',
    #             parse_mode="Markdown")
    #     if d['status'] == 'finished':
    #         file_name = d["filename"]
    #         mp3file = os.path.splitext(file_name)[0] + '.mp3'
    #         conf = 'MP3'
    #         param = mp3file
    #         m1.json_write(conf, param)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


    config = m1.json_read()
    mp3file = config['MP3']

    await bot.send_audio(chat_id=message.chat.id, audio=open(mp3file, 'rb'), reply_markup=keyboard_menu())

async def f_shazam_to_mp3(message: types.Message):
    text = message.text
    link = text[26:]
    link = re.sub(
        r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s'!()\[\]{};:'".,<>?«»""‘]))''',
        " ", link)
    title = link[:-3]
    videosSearch = VideosSearch(title, limit=1)
    YT = videosSearch.result()
    url = YT['result'][0].get('link')
    mp3file = m1.yt_download(url)
    if mp3file is None:
        await message.reply(text='Its too long!', reply_markup=keyboard_main(), disable_web_page_preview=True)
    else:
        await bot.send_audio(chat_id=message.chat.id, audio=open(mp3file, 'rb'), reply_markup=keyboard_menu())

async def f_delete_files(message: types.Message):
    FOLDER = './FILES'
    try:
        for root, dirs, files in os.walk(FOLDER):
            for file in files:
                p = os.path.join(root, file)
                if os.path.isfile(p):
                    os.remove(p)
        await message.reply(text='✅ Files successfully cleared!', disable_web_page_preview=True)
    except Exception as e:
        await message.reply(text=f'❌ Failed to delete %s. Reason: {e}')

def rate_limit(limit: int, key=None):
    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func
    return decorator

############################ MAIN ########################################
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    try:
        await dp.throttle('start', rate=4)
    except Throttled:
        await message.reply('Too many requests!')
    else:
        await message.reply(text=f'Hello, {message.from_user.username}! Iam ready to start!', reply_markup=keyboard_main())


@dp.message_handler(filters.Command(commands=['send_to_father'], ignore_caption=True))
async def command_start_handler(message: types.Message):
    await message.reply(text=f'Father!', reply_markup=keyboard_main())

@dp.message_handler(content_types=types.ContentTypes.DOCUMENT | ContentTypes.AUDIO | ContentTypes.PHOTO)
async def func_doc(message: types.Message):
    file_id = ''
    file_name = ''
    if message.photo:
        file_id = message.photo[3].file_id
        FILENAME = f'foto{randrange(10000)}.jpg'
        FILE_PATH = f'./FILES/{FILENAME}'
        await bot.download_file_by_id(file_id, destination=FILE_PATH)
        try:
            d1.upload_file(FILE_PATH, FILENAME)
            await message.reply(text='✅ Photo successfully saved to Dropbox!', disable_web_page_preview=True)
        except Exception as e:
            await bot.send_message(message.from_user.id, text=f'❌  Error: {e}...',
                                   reply_to_message_id=message.message_id)
    else:
        if message.document:
            file_id = message.document.file_id
            file_name = message.document["file_name"]
        if message.video:
            file_id = message.video.file_id
            file_name = message.video["file_name"]
        if message.audio:
            file_id = message.audio.file_id
            file_name = message.audio["file_name"]
            duration = message.audio.duration
        FILE_PATH = f'./FILES/{file_name}'
        FILENAME = file_name
        try:
            await bot.download_file(file_id, destination=FILE_PATH)
            d1.upload_file(FILE_PATH, FILENAME)
            await message.reply(text='✅ File successfully saved to Dropbox!', disable_web_page_preview=True)
        except Exception as e:
            await bot.send_message(message.from_user.id, text=f'❌  Error: {e}...',
                                   reply_to_message_id=message.message_id)




#@dp.message_handler(filters.Regexp(REGEX_UT))
#async def regexp_example(message: types.Message):
#    await message.reply(text=f'_Got Youtube link, start downloading mp3!_', #parse_mode="Markdown")
#    await f_yot_to_mp3(message)
#    await f_delete(message)
#    await message.reply(text=f'_Done!_', parse_mode="Markdown")

# @dp.message_handler(filters.Text(contains='shazam'))
# async def regexp_2(message: types.Message):
#     await message.reply(text=f'_Got Shazam link, start downloading mp3!_', parse_mode="Markdown")
#     await f_shazam_to_mp3(message)
#     await message.reply(text=f'_Done!_', parse_mode="Markdown")

@dp.message_handler()
@dp.edited_message_handler()
async def all_message(message: types.Message):
    USR = ''
    if message.text == '📋 MyData':
        try:
            await dp.throttle('📋 MyData', rate=3)
        except Throttled:
            await message.reply('Too many requests!')
        else:
            await f_mydata(message)
    elif message.text == '♻ Flush FILES':
        await f_delete_files(message)
    elif message.text == '❌ Cancel':
        await bot.send_message(message.from_user.id, text='✅ Start!', reply_markup=keyboard_main())
    elif message.text == '⚙ ACTION':
        await bot.send_message(message.from_user.id, text='What you want to do?', reply_markup=keyboard_menu(), reply_to_message_id=message.message_id)
    else:
        date_and_time = datetime.datetime(2020, 2, 19, 12, 0, 0)
        if message.forward_sender_name:
            USR = message.forward_sender_name
            print(USR)
        try:
            with open("./INFO/INFO.txt", "a") as myfile:
                myfile.write(f'NEW ({date_and_time}, FROM {USR}):{message.text}\n')
            await bot.send_message(message.from_user.id, text='✅ Text added to note!', reply_to_message_id=message.message_id)
        except Exception as e:
            await bot.send_message(message.from_user.id, text=f'❌  Error: {e}...',
                                   reply_to_message_id=message.message_id)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

