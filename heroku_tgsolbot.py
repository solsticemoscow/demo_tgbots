from module_main_fuctions import MODULE_MAIN
from module_todoist import TODOIS_MODULE
from module_dropbox import DROPBOX_MODULE
from module_mail import MAIL_MODULE
from config_con import *


import re, os, time
import youtube_dl
import os
import translators as ts


import telebot

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, DispatcherHandlerStop
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)


############################### variables ###########################################

m1 = MODULE_MAIN()
td1 = TODOIS_MODULE()
d1 = DROPBOX_MODULE()
mail1 = MAIL_MODULE()

PORT = int(os.environ.get('PORT', '8443'))
TODOLIST_API = os.environ.get('TODOLIST_API')
TOKEN = os.environ.get('TELEGRAM_SOLBOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

def key_reply_start():
    button_start = KeyboardButton('π MENU')
    button_faq = KeyboardButton('β FAQ')
    button_test = KeyboardButton('π¬ TEST')
    button_chatbot = KeyboardButton('π€ Talk to Chatbot')
    keyboard = ReplyKeyboardMarkup([[button_start, button_test], [button_chatbot]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def key_reply_main():
    button_menu = KeyboardButton('π MENU')
    button_test = KeyboardButton('π¬ TEST')
    button_mydata = KeyboardButton('π My Data')
    button_translate = KeyboardButton('πΊπΈ-π·πΊ Translate')
    button_chatbot = KeyboardButton('π€ Talk to Chatbot')
    button_back = KeyboardButton('π Back')
    button_stt = KeyboardButton('π STT & TTS')
    keyboard = ReplyKeyboardMarkup([[button_mydata, button_chatbot], [button_stt, button_translate]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def key_reply_short():
    button_menu = KeyboardButton('π MENU')
    keyboard = ReplyKeyboardMarkup([[button_menu]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def key_reply_text():
    button2 = KeyboardButton('β° Add note')
    button3 = KeyboardButton('π§ Send mail')
    button4 = KeyboardButton('π Add contact')
    button_cancel = KeyboardButton('β Cancel')
    keyboard = ReplyKeyboardMarkup([[button2], [button3, button4], [button_cancel]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def f_start(update, context):
    context.bot.deleteMessage(update.message.chat.id, message_id=update.message.message_id - 1)
    context.bot.deleteMessage(update.message.chat.id, message_id=update.message.message_id)
    context.bot.send_message(update.message.chat.id, text="β‘ Get ready? Set action and Go!",
                             reply_markup=key_reply_start())

def f_main(update, context):
    context.bot.deleteMessage(update.message.chat.id, message_id=update.message.message_id-1)
    context.bot.deleteMessage(update.message.chat.id, message_id=update.message.message_id)
    context.bot.send_message(update.message.chat.id, text='β Set action',
                             reply_markup=key_reply_main())

def f_mydata(update, context):
    context.bot.deleteMessage(update.message.chat.id, message_id=update.message.message_id-1)
    context.bot.send_message(update.message.chat.id,
                                 text=f'`alexander.tsyrkun@gmail.com`\n\n'
                                 f'`sanchez01@mail.ru`\n\n'
                                 f'`123qweASD!`\n\n'
                                 f'`solstice@solmusic.moscow`',
                                 parse_mode="Markdown",
                                 reply_markup=key_reply_short())

def f_yt1(update, context):
    utlink = update.message.text
    context.bot.deleteMessage(update.message.chat.id, message_id=update.message.message_id)

    def get_info(utlink):
        d = {
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }
            ]
        }
        ydl = youtube_dl.YoutubeDL(d)

        with ydl:
            result = ydl.extract_info(utlink, download=False)
            for index, (key, value) in enumerate(result.items()):
                if key == 'duration':
                    duration = value
                    conf = 'DURATION'
                    param = duration
                    m1.json_write(conf, param)
                if key == 'title':
                    title = value
                    conf = 'TITLE'
                    param = title
                    m1.json_write(conf, param)

    get_info(utlink)
    config = m1.json_read()
    duration = config['DURATION']
    title = config['TITLE']

    if duration > 480:
        context.bot.send_message(update.message.chat.id, text='β Set action',
                                 reply_markup=key_reply_main())
    else:
        context.bot.send_message(chat_id=update.message.chat.id, text=f'β Got youtube link!',
                                 parse_mode="Markdown")
        MSG_UT = update.message.message_id
        MSG = update.message.message_id + 1

        link = m1.regex_yt(utlink)

        def my_hook(d):
            if d['status'] == 'downloading':
                context.bot.edit_message_text(
                    chat_id=update.message.chat.id,
                    message_id=MSG,
                    text=f'β *Title*:\n\n_{title}_\n\nπ₯ *Progress*:_{d["_percent_str"]}_ with speed: _{d["_speed_str"]}_',
                    parse_mode="Markdown")
            if d['status'] == 'finished':
                file_name = d["filename"]
                mp3file = os.path.splitext(file_name)[0] + '.mp3'
                conf = 'MP3'
                param = mp3file
                m1.json_write(conf, param)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [my_hook],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        config = m1.json_read()
        mp3file = config['MP3']

        context.bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=MSG,
            text=f'β *Done!* _Sending audiofile..._',
            parse_mode="Markdown")

        context.bot.send_audio(update.message.chat.id, audio=open(mp3file, 'rb'), title=mp3file[:-16],
                               duration=duration)
        context.bot.deleteMessage(update.message.chat.id, message_id=MSG)
        context.bot.deleteMessage(update.message.chat.id, message_id=MSG_UT)

        mypath = "./"
        for root, dirs, files in os.walk(mypath):
            for file in files:
                p = os.path.join(root, file)
                if os.path.isfile(p):
                    if p[-4:] == ".mp3":
                        os.remove(p)


def f_text(bot, update):
    config = m1.json_read()
    CHATBOTSTATE = config['CHATBOTSTATE']
    if CHATBOTSTATE == 'on':
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(DIALOGFLOW_PROJECT_ID, DIALOGFLOW_SESSION_ID)
        text_input = TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE)
        query_input = QueryInput(text=text_input)
        try:
            response = session_client.detect_intent(session=session, query_input=query_input)
        except InvalidArgument:
            raise
        print("Query text:", response.query_result.query_text)
        print("Detected intent:", response.query_result.intent.display_name)
        print("Detected intent confidence:", response.query_result.intent_detection_confidence)
        print("Fulfillment text:", response.query_result.fulfillment_text)
        if response.query_result.fulfillment_text == '':
            bot.message.reply_text('ΠΠ΅ ΠΏΠΎΠ½ΠΈΠΌΠ°Ρ ΡΠ΅Π±Ρ, ΠΏΠΎΠΏΡΠΎΠ±ΡΠΉ Π΅ΡΡ.')
        else:
            bot.message.reply_text(response.query_result.fulfillment_text)
    if CHATBOTSTATE == 'off':
        if bot.message.document:
            print('DOC!!')
        else:
            conf = 'NOTE_TEXT'
            param = bot.message.text
            m1.json_write(conf, param)
            conf = 'NOTE_FILE_CHECK'
            param = False
            m1.json_write(conf, param)
            bot.message.reply_text('β What to do?', reply_markup=key_reply_text(), quote=True)

def f_other(update, context):
    context.bot.deleteMessage(update.message.chat.id, message_id=update.message.message_id)
    msg = update.message
    conf = 'NOTE_FILE_CHECK'
    param = True
    m1.json_data(conf, param)
    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document["file_name"]
        FILE_PATH = f'./FILES/{file_name}'
        FILE_NAME = file_name
        conf = 'NOTE_FILE_PATH'
        param = FILE_PATH
        m1.json_data(conf, param)
        conf = 'NOTE_FILE_NAME'
        param = FILE_NAME
        m1.json_data(conf, param)
        try:
            new_file = context.bot.getFile(file_id)
            new_file.download(FILE_PATH)
        except Exception as e:
            print(e)
        update.message.reply_text('β  What to do with doc?', reply_markup=key_reply_text1(), reply_to_message_id=update.message.message_id)
    if update.message.photo:
        file_id = update.message.photo[-1]
        FILE_NAME = f'{update.message.photo[-1]["file_unique_id"]}.jpg'
        FILE_PATH = f'./FILES/{FILE_NAME}'
        conf = 'NOTE_FILE_PATH'
        param = FILE_PATH
        m1.json_data(conf, param)
        conf = 'NOTE_FILE_NAME'
        param = FILE_NAME
        m1.json_data(conf, param)
        try:
            new_file = context.bot.getFile(file_id)
            new_file.download(FILE_PATH)
        except Exception as e:
            print(e)
        update.message.reply_text('β  What to do with photo?', reply_markup=key_reply_text1(), reply_to_message_id=update.message.message_id)
    if update.message.audio:
        file_id = update.message.audio.file_id
        FILE_NAME = str(file_id) + ".mp3"
        FILE_PATH = f'./FILES/{FILE_NAME}'
        conf = 'NOTE_FILE_PATH'
        param = FILE_PATH
        m1.json_data(conf, param)
        conf = 'NOTE_FILE_NAME'
        param = FILE_NAME
        m1.json_data(conf, param)
        try:
            new_file = context.bot.getFile(file_id)
            new_file.download(FILE_PATH)
        except Exception as e:
            print(e)
        update.message.reply_text('β  What to do with audio?', reply_markup=key_reply_text1(), reply_to_message_id=update.message.message_id)
    if update.message.voice:
        file_id = update.message.voice.file_id
        FILE_NAME = str(file_id) + ".ogg"
        FILE_PATH = f'./FILES/{FILE_NAME}'
        conf = 'NOTE_FILE_PATH'
        param = FILE_PATH
        m1.json_data(conf, param)
        conf = 'NOTE_FILE_NAME'
        param = FILE_NAME
        m1.json_data(conf, param)
        try:
            new_file = context.bot.getFile(file_id)
            new_file.download(FILE_PATH)
        except Exception as e:
            print(e)
        update.message.reply_text('β  What to do with voice?', reply_markup=key_reply_text1(), reply_to_message_id=update.message.message_id)
    if update.message.video:
        file_id = update.message.video.file_id
        FILE_NAME = str(file_id) + ".mp4"
        FILE_PATH = f'./FILES/{FILE_NAME}'
        conf = 'NOTE_FILE_PATH'
        param = FILE_PATH
        m1.json_data(conf, param)
        conf = 'NOTE_FILE_NAME'
        param = FILE_NAME
        m1.json_data(conf, param)
        try:
            new_file = context.bot.getFile(file_id)
            new_file.download(FILE_PATH)
        except Exception as e:
            print(e)
        update.message.reply_text('β  What to do with video?', reply_markup=key_reply_text1(), reply_to_message_id=update.message.message_id)
    else:
        conf = 'NOTE'
        param = update.message.text
        config = m1.json_data(conf, param)
############################ Keyboards reply ########################################


##### W

def key_reply_t1():
    button1 = KeyboardButton('π MUSIC')
    button2 = KeyboardButton('π IT')
    button3 = KeyboardButton('π OTHER')
    button_cancel = KeyboardButton('β Cancel')
    keyboard = ReplyKeyboardMarkup([[button1, button2, button3], [button_cancel]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def key_reply_t2():
    button1 = KeyboardButton('π TASK_DATA')
    button2 = KeyboardButton('π TASK_IT_PYTHON')
    button3 = KeyboardButton('π TASK_IT_INFO')
    button_back = KeyboardButton('π Back')
    button_cancel = KeyboardButton('β Cancel')
    keyboard = ReplyKeyboardMarkup([[button1], [button2], [button3], [button_back, button_cancel]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def key_reply_t3():
    button1 = KeyboardButton('π TASK_MUSIC')
    button2 = KeyboardButton('π TASK_PRODUCTION')
    button_back = KeyboardButton('π Back')
    button_cancel = KeyboardButton('β Cancel')
    keyboard = ReplyKeyboardMarkup([[button1], [button2], [button_back, button_cancel]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def key_reply_t4():
    button1 = KeyboardButton('π TASK_OTHER')
    button2 = KeyboardButton('π TASK_SEX')
    button_back = KeyboardButton('π Back')
    button_cancel = KeyboardButton('β Cancel')
    keyboard = ReplyKeyboardMarkup([[button1], [button2], [button_back, button_cancel]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def f_task_start(update, context):
    update.message.reply_text('π Enter title:', reply_markup=ReplyKeyboardRemove())
    return "STEP1"

def f_task1(update, context):
    conf = 'NOTE_TITLE'
    param = update.message.text
    m1.json_data(conf, param)
    update.message.reply_text('π Select Project:', reply_markup=key_reply_t1())
    return "STEP2"

def f_task2(update, context):
    project_name = update.message.text
    if project_name == 'π IT':
        update.message.reply_text('π Select Task:', reply_markup=key_reply_t2())
        return "STEP3"
    if project_name == 'π MUSIC':
        update.message.reply_text('π Select Task:', reply_markup=key_reply_t3())
        return "STEP3"
    if project_name == 'π OTHER':
        update.message.reply_text('π Select Task:', reply_markup=key_reply_t4())
        return "STEP3"
    if project_name == 'β Cancel':
        context.bot.send_message(update.message.chat.id, text='β Cancelled by user')
        return ConversationHandler.END

def f_task3(update, context):
    input_text = update.message.text
    m1.delete_files(path='FILES')
    if input_text == 'π TASK_MUSIC':
        config = m1.json_data()
        NOTE_FILE_CHECK = config['NOTE_FILE_CHECK']
        if NOTE_FILE_CHECK is False:
            config = m1.json_data()
            NOTE_TEXT = config['NOTE_TEXT']
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\nText:\n\n{NOTE_TEXT}'
            td1.add_comment_text(TODOLIST_TASK_MUSIC, COMMENT)
        elif NOTE_FILE_CHECK is True:
            config = m1.json_data()
            NOTE_FILE_PATH = config['NOTE_FILE_PATH']
            NOTE_FILE_NAME = config['NOTE_FILE_NAME']
            PATH_TO_DISPLAY = d1.drop_upload_file(FILE=NOTE_FILE_PATH, PATHTO=f'/INFO/MUSIC/TASK_MUSIC/{NOTE_FILE_NAME}')
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\n\nAttachment dropbox link:\n{PATH_TO_DISPLAY}'
            td1.add_comment_text(TODOLIST_TASK_MUSIC, COMMENT)
        update.message.reply_text('βοΈComment added!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    if input_text == 'π TASK_PRODUCTION':
        config = m1.json_data()
        NOTE_FILE_CHECK = config['NOTE_FILE_CHECK']
        if NOTE_FILE_CHECK is False:
            config = m1.json_data()
            NOTE_TEXT = config['NOTE_TEXT']
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\nText:\n\n{NOTE_TEXT}'
            td1.add_comment_text(TODOLIST_TASK_PRODUCTION, COMMENT)
        elif NOTE_FILE_CHECK is True:
            config = m1.json_data()
            NOTE_FILE_PATH = config['NOTE_FILE_PATH']
            NOTE_FILE_NAME = config['NOTE_FILE_NAME']
            PATH_TO_DISPLAY = d1.drop_upload_file(FILE=NOTE_FILE_PATH, PATHTO=f'/INFO/MUSIC/TASK_PRODUCTION/{NOTE_FILE_NAME}')
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\n\nAttachment dropbox link:\n{PATH_TO_DISPLAY}'
            td1.add_comment_text(TODOLIST_TASK_PRODUCTION, COMMENT)
        update.message.reply_text('βοΈComment added!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    if input_text == 'π TASK_OTHER':
        config = m1.json_data()
        NOTE_FILE_CHECK = config['NOTE_FILE_CHECK']
        if NOTE_FILE_CHECK is False:
            config = m1.json_data()
            NOTE_TEXT = config['NOTE_TEXT']
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\nText:\n\n{NOTE_TEXT}'
            td1.add_comment_text(TODOLIST_TASK_OTHER, COMMENT)
        elif NOTE_FILE_CHECK is True:
            config = m1.json_data()
            NOTE_FILE_PATH = config['NOTE_FILE_PATH']
            NOTE_FILE_NAME = config['NOTE_FILE_NAME']
            PATH_TO_DISPLAY = d1.drop_upload_file(FILE=NOTE_FILE_PATH, PATHTO=f'/INFO/OTHER/TASK_OTHER/{NOTE_FILE_NAME}')
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\n\nAttachment dropbox link:\n{PATH_TO_DISPLAY}'
            td1.add_comment_text(TODOLIST_TASK_OTHER, COMMENT)
        update.message.reply_text('βοΈComment added!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    if input_text == 'π TASK_SEX':
        config = m1.json_data()
        NOTE_FILE_CHECK = config['NOTE_FILE_CHECK']
        if NOTE_FILE_CHECK is False:
            config = m1.json_data()
            NOTE_TEXT = config['NOTE_TEXT']
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\nText:\n\n{NOTE_TEXT}'
            td1.add_comment_text(TODOLIST_TASK_SEX, COMMENT)
        elif NOTE_FILE_CHECK is True:
            config = m1.json_data()
            NOTE_FILE_PATH = config['NOTE_FILE_PATH']
            NOTE_FILE_NAME = config['NOTE_FILE_NAME']
            PATH_TO_DISPLAY = d1.drop_upload_file(FILE=NOTE_FILE_PATH, PATHTO=f'/INFO/OTHER/TASK_SEX/{NOTE_FILE_NAME}')
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\n\nAttachment dropbox link:\n{PATH_TO_DISPLAY}'
            td1.add_comment_text(TODOLIST_TASK_SEX, COMMENT)
        update.message.reply_text(f'βοΈComment added! URL:\n\n'
                                  f'https://todoist.com/app/project/2276636316/task/5302503083/comments#', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    if input_text == 'π TASK_IT_INFO':
        config = m1.json_data()
        NOTE_FILE_CHECK = config['NOTE_FILE_CHECK']
        if NOTE_FILE_CHECK is False:
            config = m1.json_data()
            NOTE_TEXT = config['NOTE_TEXT']
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\nText:\n\n{NOTE_TEXT}'
            td1.add_comment_text(TODOLIST_TASK_IT_INFO, COMMENT)
        elif NOTE_FILE_CHECK is True:
            config = m1.json_data()
            NOTE_FILE_PATH = config['NOTE_FILE_PATH']
            NOTE_FILE_NAME = config['NOTE_FILE_NAME']
            PATH_TO_DISPLAY = d1.drop_upload_file(FILE=NOTE_FILE_PATH, PATHTO=f'/INFO/IT/TASK_IT_INFO/{NOTE_FILE_NAME}')
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\n\nAttachment dropbox link:\n{PATH_TO_DISPLAY}'
            td1.add_comment_text(TODOLIST_TASK_IT_INFO, COMMENT)
        update.message.reply_text('βοΈComment added!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    if input_text == 'π TASK_IT_PYTHON':
        config = m1.json_data()
        NOTE_FILE_CHECK = config['NOTE_FILE_CHECK']
        if NOTE_FILE_CHECK is False:
            config = m1.json_data()
            NOTE_TEXT = config['NOTE_TEXT']
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\nText:\n\n{NOTE_TEXT}'
            td1.add_comment_text(TODOLIST_TASK_IT_PYTHON, COMMENT)
        elif NOTE_FILE_CHECK is True:
            config = m1.json_data()
            NOTE_FILE_PATH = config['NOTE_FILE_PATH']
            NOTE_FILE_NAME = config['NOTE_FILE_NAME']
            PATH_TO_DISPLAY = d1.drop_upload_file(FILE=NOTE_FILE_PATH, PATHTO=f'/INFO/IT/TASK_IT_PYTHON/{NOTE_FILE_NAME}')
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\n\nAttachment dropbox link:\n{PATH_TO_DISPLAY}'
            td1.add_comment_text(TODOLIST_TASK_IT_PYTHON, COMMENT)
        update.message.reply_text('βοΈComment added!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    if input_text == 'π TASK_DATA':
        config = m1.json_data()
        NOTE_FILE_CHECK = config['NOTE_FILE_CHECK']
        if NOTE_FILE_CHECK is False:
            config = m1.json_data()
            NOTE_TEXT = config['NOTE_TEXT']
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\nText:\n\n{NOTE_TEXT}'
            td1.add_comment_text(TODOLIST_TASK_IT_DATA, COMMENT)
        elif NOTE_FILE_CHECK is True:
            config = m1.json_data()
            NOTE_FILE_PATH = config['NOTE_FILE_PATH']
            NOTE_FILE_NAME = config['NOTE_FILE_NAME']
            PATH_TO_DISPLAY = d1.drop_upload_file(FILE=NOTE_FILE_PATH, PATHTO=f'/INFO/IT/TASK_IT_DATA/{NOTE_FILE_NAME}')
            NOTE_TITLE = config['NOTE_TITLE']
            COMMENT = f'{NOTE_TITLE}\n\nAttachment dropbox link:\n{PATH_TO_DISPLAY}'
            td1.add_comment_text(TODOLIST_TASK_IT_DATA, COMMENT)
        update.message.reply_text('βοΈComment added!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    if input_text == 'π Back':
        context.bot.send_message(update.message.chat.id, text="Try:")
        return "STEP1"
    if input_text == 'β Cancel':
        context.bot.send_message(update.message.chat.id, text='β Cancelled by user')
        return ConversationHandler.END

def f_task_cancel(update, context):
    context.bot.send_message(update.message.chat.id, text="CANCEL", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

##### W

def f_task_mail(update, context):
    update.message.reply_text('ΠΠ°ΠΊΠ°Ρ ΡΠ΅ΠΌΠ° ΡΠΎΠΎΠ±ΡΠ΅Π½ΠΈΡ?')
    return "STEP7"

def f_task_mail2(update, context):
    email_sbj = update.message.text
    config = m1.load_json_data('./config_var.json')
    config['EMAIL_SBJ'] = email_sbj
    m1.save_json_data(config, './config_var.json')
    update.message.reply_text('ΠΠ° ΠΊΠ°ΠΊΠΎΠΉ ΡΡΠΈΠΊ ΠΎΡΠΏΡΠ°Π²Π»ΡΡΡ? ΠΠ²Π΅Π΄ΠΈ Π²ΡΡΡΠ½ΡΡ ΠΈΠ»ΠΈ Π²ΡΠ±Π΅ΡΠΈ ΠΈΠ· ΡΠΏΠΈΡΠΊΠ°:',
                              reply_markup=key_reply_mail())
    return "STEP8"

def f_task_mail3(update, context):
    email_to = update.message.text
    config = m1.load_json_data('./config_var.json')
    email_text = config['TASK_TEXT']
    email_sbj = config['EMAIL_SBJ']
    # email_att = config['FILES_PATH']
    result = mail1.send_simple_text_mail(text=email_text, to=email_to, sbj=email_sbj)
    print(f'result: {result}')
    if result == 'OK!':
        context.bot.send_message(update.message.chat.id, text="ΠΠΈΡΡΠΌΠΎ ΡΡΠΏΠ΅ΡΠ½ΠΎ ΠΎΡΠΏΡΠ°Π²Π»Π΅Π½ΠΎ!",
                                 reply_markup=key_reply_main1())
    else:
        context.bot.send_message(update.message.chat.id, text="ΠΡΠΈΠ±ΠΊΠ°...",
                                 reply_markup=key_reply_main1())
    return ConversationHandler.END

def f_task_contact(update, context):
    NEW_CONTACT = update.message.text

    contact = InputPhoneContact(client_id=0, phone=NEW_CONTACT, first_name="ABC", last_name="abc")
    result = client.invoke(ImportContactsRequest([contact], replace=True))

def f_task_cancel(update, context):
    context.bot.send_message(update.message.chat.id, text="ΠΠ±ΡΠ°Π±Π°ΡΡΠ²Π°Π΅ΡΡΡ ΡΠ΅ΠΊΡΡ Π΄Π°Π»ΡΡΠ΅", reply_markup=key_reply_start())
    return ConversationHandler.END

################ TRASLATE
def f_translate_start(update, _):
    update.message.reply_text('β© ΠΡΠ±Π΅ΡΠΈ Π½Π°ΠΏΡΠ°Π²Π»Π΅Π½ΠΈΠ΅ ΠΏΠ΅ΡΠ΅Π²ΠΎΠ΄Π°:',
                              reply_markup=key_reply_translate())
    return "INPUTTEXT"


def f_translate_ln(update, context):
    input_text = update.message.text
    if input_text == 'πΊπΈEN->RUπ·πΊ':
        update.message.reply_text('ΠΡΠΏΡΠ°Π²Ρ Π±ΠΎΡΡ ΡΠ΅ΠΊΡΡ Π΄Π»Ρ ΠΏΠ΅ΡΠ΅Π²ΠΎΠ΄Π° (πΊπΈEN):',
                                  reply_markup=ReplyKeyboardRemove())
        return "ENRU"
    if input_text == 'π·πΊRU->ENπΊπΈ':
        update.message.reply_text('ΠΡΠΏΡΠ°Π²Ρ Π±ΠΎΡΡ ΡΠ΅ΠΊΡΡ Π΄Π»Ρ ΠΏΠ΅ΡΠ΅Π²ΠΎΠ΄Π° (π·πΊRU):\n',
                                  reply_markup=ReplyKeyboardRemove())
        return "RUEN"


def f_translate_enru(update, context):
    input_text = update.message.text
    input_text_message_id = update.message.message_id
    output_text = ts.google(input_text, from_language='en', to_language='ru')

    context.bot.send_message(
        update.message.chat.id,
        text=f'βοΈΠΠ΅ΡΠ΅Π²ΠΎΠ΄:\n\n'
        f'`{output_text}`\n\n'
        f'*Tip*: ΠΠ»ΠΈΠΊΠ½ΠΈ Π½Π° ΡΠ΅ΠΊΡΡ ΠΏΠ΅ΡΠ΅Π²ΠΎΠ΄Π°, ΡΡΠΎΠ±Ρ Π±ΡΡΡΡΠΎ ΡΠΊΠΎΠΏΠΈΡΠΎΠ²Π°ΡΡ'
        f'(_Π’ΠΎΠ»ΡΠΊΠΎ Π½Π° ΠΌΠΎΠ±ΠΈΠ»ΡΠ½ΡΡ ΡΡΡΡΠΎΠΉΡΡΠ²Π°Ρ_)',
        parse_mode="Markdown",
        reply_markup=key_reply_translate2(),
        reply_to_message_id=input_text_message_id)
    return ConversationHandler.END


def f_translate_ruen(update, context):
    input_text = update.message.text
    input_text_message_id = update.message.message_id
    output_text = ts.google(input_text, from_language='ru', to_language='en')

    context.bot.send_message(
        update.message.chat.id,
        text=f'βοΈΠΠ΅ΡΠ΅Π²ΠΎΠ΄:\n\n'
        f'`{output_text}`\n\n'
        f'*Tip*: ΠΠ»ΠΈΠΊΠ½ΠΈ Π½Π° ΡΠ΅ΠΊΡΡ ΠΏΠ΅ΡΠ΅Π²ΠΎΠ΄Π°, ΡΡΠΎΠ±Ρ Π±ΡΡΡΡΠΎ ΡΠΊΠΎΠΏΠΈΡΠΎΠ²Π°ΡΡ'
        f'(_Π’ΠΎΠ»ΡΠΊΠΎ Π½Π° ΠΌΠΎΠ±ΠΈΠ»ΡΠ½ΡΡ ΡΡΡΡΠΎΠΉΡΡΠ²Π°Ρ_)',
        parse_mode="Markdown",
        reply_markup=key_reply_translate2(),
        reply_to_message_id=input_text_message_id)
    return ConversationHandler.END


def f_translate_cancel(update, context):
    context.bot.send_message(update.message.chat.id,
                             text="β ΠΠ΅ΡΠ΅Π²ΠΎΠ΄ ΠΎΡΠΌΠ΅Π½ΡΠ½",
                             reply_markup=key_reply_main1())
    return ConversationHandler.END


################ TTS


def f_tts_start(update, context):
    # print(f'f_tts_start: {update.message}')
    context.bot.deleteMessage(update.message.chat.id,
                              message_id=update.message.message_id)
    update.message.reply_text(
        'ΠΡΠ±Π΅ΡΠΈ Π½Π°ΠΏΡΠ°Π²Π»Π΅Π½ΠΈΠ΅ ΠΊΠΎΠ½Π²Π΅ΡΡΠ°ΡΠΈΠΈ:\n'
        '1. Speech to Text - Π³ΠΎΠ»ΠΎΡΠΎΠ²ΡΠ΅ ΡΠΎΠΎΠ±ΡΠ΅Π½ΠΈΠ΅ ΠΊΠΎΠ½Π²Π΅ΡΡΠΈΡΡΡΡΡΡ Π² ΡΠ΅ΠΊΡΡ\n'
        '2. Text to Speech - ΡΠ΅ΠΊΡΡΠΎΠ²ΡΠ΅ ΡΠΎΠΎΠ±ΡΠ΅Π½ΠΈΠ΅ ΠΊΠΎΠ½Π²Π΅ΡΡΠΈΡΡΡΡΡΡ Π² Π³ΠΎΠ»ΠΎΡΠΎΠ²ΠΎΠ΅'
        '',
        reply_markup=key_reply_tts1())
    return "STEP1"


def f_tts1(update, context):
    context.bot.deleteMessage(update.message.chat.id,
                              message_id=update.message.message_id)
    input_text = update.message.text
    if input_text == 'Speech to Text':
        update.message.reply_text(
            'πΆ ΠΡΠΏΡΠ°Π²Ρ Π±ΠΎΡΡ Π³ΠΎΠ»ΠΎΡΠΎΠ²ΠΎΠ΅ ΡΠΎΠΎΠ±ΡΠ΅Π½ΠΈΠ΅ Π΄Π»Ρ ΠΊΠΎΠ½Π²Π΅ΡΡΠ°ΡΠΈΠΈ:',
            reply_markup=ReplyKeyboardRemove())
        return "STEP2"
    if input_text == 'Text to Speech':
        update.message.reply_text(
            'π ΠΡΠΏΡΠ°Π²Ρ Π±ΠΎΡΡ ΡΠ΅ΠΊΡΡ Π΄Π»Ρ ΠΊΠΎΠ½Π²Π΅ΡΡΠ°ΡΠΈΠΈ (ΠΠΎΠΊΠ° ΠΏΠΎΠ΄Π΄Π΅ΡΠΆΠΈΠ²Π°Π΅ΡΡΡ ΡΠΎΠ»ΡΠΊΠΎ ΠΊΠΈΡΡΠΈΠ»ΠΈΡΠ°):\n',
            reply_markup=ReplyKeyboardRemove())
        return "STEP2"


def f_tts2(update, context):
    input_text = update.message.text
    tts_filename = str(update.message.from_user.id)
    config = m1.load_json_data('./config_var.json')
    config['TTS_INPUT_TEXT'] = input_text
    m1.save_json_data(config, './config_var.json')
    tts_text_input = input_text
    tts = gTTS(text=tts_text_input, lang='ru')
    tts.save(f'./{tts_filename}.mp3')
    context.bot.send_message(update.message.chat.id,
                             text=f'*β Π‘Π³Π΅Π½Π΅ΡΠΈΡΠΎΠ²Π°Π½Π½ΠΎΠ΅ Π°ΡΠ΄ΠΈΠΎ:*',
                             parse_mode="Markdown",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=key_reply_tts2())

    context.bot.send_audio(update.message.chat.id,
                           audio=open(f'./{tts_filename}.mp3', 'rb'))
    path = "/"
    ext = '.mp3'
    m1.delete_files(path, ext)
    return ConversationHandler.END


def f_tts3(update, context):
    file_duration = update.message.voice.duration
    if file_duration < 2:
        update.message.reply_text(
            text=
            'ΠΠ»ΠΈΡΠ΅Π»ΡΠ½ΠΎΡΡΡ Π·Π°ΠΏΠΈΡΠΈ Π½Π΅ ΠΌΠΎΠΆΠ΅Ρ Π±ΡΡΡ ΠΊΠΎΡΠΎΡΠ΅ 2 ΡΠ΅ΠΊΡΠ½Π΄! ΠΠΎΠΏΡΠΎΠ±ΡΠΉ Π΅ΡΡ:',
            reply_markup=ReplyKeyboardRemove())
        return "STEP2"
    file = context.bot.getFile(update.message.voice.file_id)
    file_id = str(update.message.message_id)
    filename = "tts-" + file_id + ".ogg"
    path = f'./{filename}'
    file.download(path)
    config = m1.load_json_data('./config_var.json')
    config['STT_JOB_ID'] = r1.convert_start(path)
    m1.save_json_data(config, './config_var.json')
    update.message.reply_text(
        text=
        f'_β ΠΠΎΠ»ΡΡΠ΅Π½Π° Π°ΡΠ΄ΠΈΠΎΠ·Π°ΠΏΠΈΡΡ, Π½Π°ΡΠΈΠ½Π°Π΅ΡΡΡ ΠΊΠΎΠ½Π²Π΅ΡΡΠ°ΡΠΈΡ. ΠΡΠ΅ΠΌΡ ΠΊΠΎΠ½Π²Π΅ΡΡΠ°ΡΠΈΠΈ Π·Π°Π²ΠΈΡΠΈΡ ΠΎΡ Π΄Π»ΠΈΡΠ΅Π»ΡΠ½ΠΎΡΡΠΈ Π·Π°ΠΏΠΈΡΠΈ, '
        f'ΡΠ°ΠΊ ΠΊΠ°ΠΊ ΠΊΠΎΠ½Π²Π΅ΡΡΠ°ΡΠΈΡ ΠΏΡΠΎΠΈΡΡΠΎΠ΄ΠΈΡ ΠΎΠ½Π»Π°ΠΉΠ½ Π½Π° ΡΠ΅ΡΠ²Π΅ΡΠ΅, ΡΠΎ'
        f' ΠΎΠΆΠΈΠ΄Π°Π½ΠΈΠ΅ ΠΌΠΎΠΆΠ΅Ρ ΡΠΎΡΡΠ°Π²ΠΈΡΡ ΠΎΡ 15 ΡΠ΅ΠΊΡΠ½Π΄ Π΄ΠΎ ΠΌΠΈΠ½ΡΡΡ._',
        parse_mode="Markdown",
        reply_to_message_id=update.message.message_id,
        reply_markup=key_reply_tts3())
    path = "/"
    ext = '.ogg'
    m1.delete_files(path, ext)
    return "STEP3"


def f_tts_wrong(update, context):
    context.bot.send_message(update.message.chat.id,
                             text="β ΠΠ΅ΠΊΠΎΡΡΠ΅ΠΊΡΠ½ΡΠΉ Π²Π²ΠΎΠ΄, ΠΏΠΎΠ²ΡΠΎΡΠΈΡΠ΅ Π²Π²ΠΎΠ΄:")
    return "STEP2"


def f_tts4(update, context):
    input_text = update.message.text
    config = m1.load_json_data('./config_var.json')
    job_id = config['STT_JOB_ID']

    output_text = r1.convert1(job_id)
    context.bot.send_message(
        update.message.chat.id,
        text=f'βοΈ_ΠΠ΅ΡΠ΅Π²ΠΎΠ΄_:\n\n'
        f'`{output_text}`\n\n'
        f'*Tip*: ΠΠ»ΠΈΠΊΠ½ΠΈ Π½Π° ΡΠ΅ΠΊΡΡ ΠΏΠ΅ΡΠ΅Π²ΠΎΠ΄Π°, ΡΡΠΎΠ±Ρ Π±ΡΡΡΡΠΎ ΡΠΊΠΎΠΏΠΈΡΠΎΠ²Π°ΡΡ'
        f'(_Π’ΠΎΠ»ΡΠΊΠΎ Π½Π° ΠΌΠΎΠ±ΠΈΠ»ΡΠ½ΡΡ ΡΡΡΡΠΎΠΉΡΡΠ²Π°Ρ_)',
        parse_mode="Markdown",
        reply_markup=key_reply_tts2(),
        reply_to_message_id=update.message.message_id)
    return ConversationHandler.END


def f_tts_cancel(update, context):
    context.bot.send_message(update.message.chat.id,
                             text=f'_β ΠΠ΅ΠΉΡΡΠ²ΠΈΠ΅ ΠΎΡΠΌΠ΅Π½Π΅Π½ΠΎ ΠΏΠΎΠ»ΡΠ·ΠΎΠ²Π°ΡΠ΅Π»Π΅ΠΌ_',
                             parse_mode="Markdown",
                             reply_markup=key_reply_main1())
    return ConversationHandler.END


def f_talk_dialogflow_onoff(update, context):
    config = m1.load_json_data('./config_var.json')
    STATE = config['CHATBOTSTATE']
    if STATE == 'off':
        config['CHATBOTSTATE'] = 'on'
        STATE = config['CHATBOTSTATE']
        m1.save_json_data(config, './config_var.json')
        context.bot.send_message(update.message.chat.id, text=f'_π¬ Π§Π°Ρ-Π±ΠΎΡ Π°ΠΊΡΠΈΠ²ΠΈΡΠΎΠ²Π°Π½_', reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    elif STATE == 'on':
        config['CHATBOTSTATE'] = 'off'
        STATE = config['CHATBOTSTATE']
        m1.save_json_data(config, './config_var.json')
        context.bot.send_message(update.message.chat.id, text=f'_π€ Π§Π°Ρ-Π±ΠΎΡ Π΄Π΅-Π°ΠΊΡΠΈΠ²ΠΈΡΠΎΠ²Π°Π½_', reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")

def f_faq(update, context):
    context.bot.send_message(update.message.chat.id, text=f'Π­ΡΠΎΡ Π±ΠΎΡ ΡΠΏΠΎΡΠΎΠ±Π΅Π½ Π½Π° ΠΌΠ½ΠΎΠ³ΠΎΠ΅ ΠΈ Π΅Π³ΠΎ ΡΡΠ½ΠΊΡΠΈΠΎΠ½Π°Π» Π±ΡΠ΄Π΅Ρ ΡΠ°ΡΡΠΈ ΡΠΎ Π²ΡΠ΅ΠΌΠ΅Π½Π΅ΠΌ (ΡΡ ΠΏΠΎΠ»ΡΡΠΈΡΡ ΠΎΠΏΠΎΠ²Π΅ΡΠ΅Π½ΠΈΠ΅, ΠΊΠΎΠ³Π΄Π° ΡΡΠΎ-ΡΠΎ ΠΏΠΎΠ»Π΅Π·Π½ΠΎΠ΅ ΠΏΠΎΡΠ²ΠΈΡΡΡ).\n'
                                                          '_ΠΠΎΡΡΠΈ Π²ΡΠ΅ Π΄Π΅ΠΉΡΡΠ²ΠΈΡ ΡΡ ΠΌΠΎΠΆΠ΅ΡΡ ΠΎΡΡΡΠ΅ΡΡΠ²Π»ΡΡΡ Ρ ΠΏΠΎΠΌΠΎΡΡΡ ΠΊΠ½ΠΎΠΏΠΎΠΊ ΡΠΏΡΠ°Π²Π»Π΅Π½ΠΈΡ Π²Π½ΠΈΠ·Ρ_\n\n'
                                                          'π‘ ΠΠ° Π΄Π°Π½Π½ΡΠΉ ΠΌΠΎΠΌΠ΅Π½Ρ Π΄ΠΎΡΡΡΠΏΠ½Ρ ΡΠ»Π΅Π΄ΡΡΡΠΈΠ΅ ΡΡΠ½ΠΊΡΠΈΠΈ:\n'
                                                          '*1. πΊπΈ-π·πΊ ΠΠ΅ΡΠ΅Π²ΠΎΠ΄ΡΠΈΠΊ*. _ΠΠ½Π»Π°ΠΉΠ½-ΠΏΠ΅ΡΠ΅Π²ΠΎΠ΄ΡΠΈΠΊ ΡΠ΅ΠΊΡΡΠ° ΠΏΠ°ΡΡ EN-RU_\n'
                                                          '*2. π ΠΠΎΠΈ Π΄Π°Π½Π½ΡΠ΅*. _ΠΠΎΡ ΠΌΠΎΠΆΠ΅Ρ ΡΡΠ°Π½ΠΈΡΡ ΡΠ²ΠΎΠΈ Π΄Π°Π½Π½ΡΠ΅, ΠΊΠΎΡΠΎΡΡΠ΅ ΡΡ ΠΌΠΎΠΆΠ΅ΡΡ ΠΎΠ±Π½ΠΎΠ²Π»ΡΡΡ, ΡΠ΄Π°Π»ΡΡΡ, Π΄ΠΎΠ±Π°Π²Π»ΡΡΡ ΠΏΠΎ ΠΌΠ΅ΡΠ΅ Π½Π°Π΄ΠΎΠ±Π½ΠΎΡΡΠΈ. ΠΠ°Π½Π½ΡΠ΅ ΡΠΈΡΡΡΡΡΡΡ ΠΈ Π΄ΠΎΡΡΡΠΏΠ½Ρ ΡΠΎΠ»ΡΠΊΠΎ ΡΠ΅Π±Π΅_\n'
                                                          '*3. π ΠΠΎΠ½Π²Π΅ΡΡΠ΅Ρ YouTube & Shazam Π² MP3*. _ΠΡΠΏΡΠ°Π²Ρ Π±ΠΎΡΡ ΡΠΎΠΎΠ±ΡΠ΅Π½ΠΈΠ΅ Ρ Youtube-ΡΡΡΠ»ΠΊΠΎΠΉ ΠΈΠ»ΠΈ Shazam ΠΈ ΠΎΠ½ Π² ΠΎΡΠ²Π΅Ρ ΠΏΡΠΈΡΠ»ΡΡ ΡΠ΅Π±Π΅ mp3-ΡΠ°ΠΉΠ»_\n'
                                                          '*6.π ΠΠΎΠ½Π²Π΅ΡΡΠ΅Ρ STT&TTS*. _ΠΠΎΡ ΡΠΌΠ΅Π΅Ρ ΠΊΠΎΠ½Π²Π΅ΡΡΠΈΡΠΎΠ²Π°ΡΡ ΡΠ΅ΠΊΡΡ Π² Π°ΡΠ΄ΠΈΠΎ-ΡΠΎΠΎΠ±ΡΠ΅Π½ΠΈΠ΅ ΠΈ Π½Π°ΠΎΠ±ΠΎΡΠΎΡ_\n\n'
                                                          'π‘ Π’Π°ΠΊΠΆΠ΅ Π΄ΠΎΡΡΡΠΏΠ½ΠΎ ΠΊΠΎΠ½ΡΠ΅ΠΊΡΡΠ½ΠΎΠ΅ ΠΌΠ΅Π½Ρ, ΠΊΠΎΡΠΎΡΠΎΠ΅ ΠΌΠΎΠΆΠ½ΠΎ ΠΈΡΠΏΠΎΠ»ΡΠ·ΠΎΠ²Π°ΡΡ Π² Π»ΡΠ±ΠΎΠΉ ΠΌΠΎΠΌΠ΅Π½Ρ:\n'
                                                          '/s - *ΠΌΠ³Π½ΠΎΠ²Π΅Π½Π½ΡΠΉ ΠΏΠ΅ΡΠ΅ΡΠΎΠ΄ Π² ΡΡΠ°ΡΡΠΎΠ²ΠΎΠ΅ ΠΌΠ΅Π½Ρ*\n'
                                                          '/h - *FAQ*\n'
                                                          '/b - *Π°ΠΊΡΠΈΠ²Π°ΡΠΈΡ\Π΄Π΅Π°ΠΊΡΠΈΠ²Π°ΡΠΈΡ ΡΠ°Ρ-Π±ΠΎΡΠ°*\n\n'

                                                          'π‘ Π ΡΠ΅ΠΆΠΈΠΌΠ΅ Ρ ΡΠ°Ρ-Π±ΠΎΡΠΎΠΌ Π΄ΠΎΠ±Π²Π»ΡΠ΅ΡΡΡ Π΄Π΅ΠΌΠΎΠ½ΡΡΡΠ°ΡΠΈΠΎΠ½Π½ΡΠΉ ΡΠ°ΠΌΠΎΠΎΠ±ΡΡΠ°Π΅ΠΌΡΠΉ Π±ΠΎΡ, ΠΊΠΎΡΠΎΡΡΠΉ ΠΎΠ±ΡΠ°Π±Π°ΡΡΠ²Π°Π΅Ρ Π²ΡΠ΅ ΡΠΎΠΎΠ±ΡΠ΅Π½ΠΈΡ. ΠΠΎΠΊΠ° Ρ Π½Π΅Π³ΠΎ ΠΏΠΎΡΡΠΈ Π½Π΅Π»ΡΠ²ΠΎΠΉ ΠΎΠΏΡΡ, Π½ΠΎ ΡΠΎ Π²ΡΠ΅ΠΌΠ΅Π½Π΅ΠΌ Π½Π° Π±ΠΎΠ»ΡΡΠΈΡ Π΄Π°Π½Π½ΡΡ ΠΎΠ½ ΠΌΠΎΠΆΠ΅Ρ\n'
                                                          'Π½Π°ΡΡΠΈΡΡΡΡ Π²Π΅ΡΡΠΈ ΡΠ΅Π±Ρ ΠΊΠ°ΠΊ Π½Π°ΡΡΠΎΡΡΠΈΠΉ ΡΠΎΠ±Π΅ΡΠ΅Π΄Π½ΠΈΠΊ, ΠΏΠΎΠ½ΠΈΠΌΠ°ΡΡΠΈΠΉ ΠΊΠΎΠ½ΡΠ΅ΠΊΡΡ ΠΈ Π°ΡΠ΄ΠΈΠΎΡΠΎΠΎΠ±ΡΠ΅Π½ΠΈΡ ΠΈ ΡΠΌΠΎΠΆΠ΅Ρ Π²ΡΠΏΠΎΠ»Π½ΡΡΡ ΠΊΠΎΠΌΠ°Π½Π΄Ρ.', parse_mode="Markdown", reply_markup=key_reply_start())

def f_test(update, context):
    cur_m = update.message.message_id + 10

    def get_10_mes(cur_m):
        list = []
        for i in range(30):
            m = cur_m - i
            try:
                context.bot.deleteMessage(update.message.chat.id, message_id=m)
            except Exception as e:
                print(e)

    try:
        get_10_mes(cur_m)
    except Exception as e:
        print(e)

##### W


##### W

def f_voice(update, context):
    file = context.bot.getFile(update.message.voice.file_id)
    file_id = str(update.message.message_id)
    filename = "tts-" + file_id + ".ogg"
    path = f'./FILES/TTS/{filename}'
    try:
        file.download(path)
    except:
        raise
    update.message.reply_text('Π‘ΠΎΠ·Π΄Π°ΡΡ Π·Π°ΠΌΠ΅ΡΠΊΡ ΠΈΠ»ΠΈ Π½Π°ΠΏΠΎΠΌΠΈΠ½Π°Π½ΠΈΠ΅?', reply_markup=key_reply_reminder(),
                           reply_to_message_id=update.message.message_id)

def f_photo(update, context):
    file = context.bot.getFile(update.message.photo[-1])
    file_id = str(update.message.message_id)
    path = f'./FILES/{file_id}.jpg'
    config = m1.load_json_data('./config_var.json')
    config['FILES_PATH'] = path
    config['FILES_ATT'] = True
    m1.save_json_data(config, './config_var.json')
    file.download(path)
    context.bot.send_photo(update.message.chat.id, photo=open(f'./FILES/{file_id}.jpg', 'rb'))

    update.message.reply_text('Π§ΡΠΎ Π΄Π΅Π»Π°ΡΡ Ρ ΡΠΎΡΠΎ?', reply_markup=key_reply_reminder(),
                           reply_to_message_id=update.message.message_id)

def f_document(update, context):
    file_id = update.message.document.file_id
    file_name = update.message.document["file_name"]
    mime_type = update.message.document["mime_type"]
    file_size = update.message.document["file_size"]
    FILE_PATH = f'./FILES/{file_name}'
    print(f' File: {file_name}\n{mime_type}\n{FILE_PATH}')
    try:
        new_file = context.bot.getFile(file_id)
        new_file.download(FILE_PATH)
    except Exception as e:
        print(e)
    result = d1.drop_upload_file(FILE=FILE_PATH, PATHTO=f'/INFO/TEST/{file_name}')
    print(result)


    # path = f'./FILES/{file_id}.f'
    # file.download(path)
    # context.bot.send_photo(update.message.chat.id, photo=open(f'./FILES/{file_id}.pdf', 'rb'))
    #
    # update.message.reply_text('Π‘ΠΎΠ·Π΄Π°ΡΡ Π·Π°ΠΌΠ΅ΡΠΊΡ ΠΈΠ»ΠΈ Π½Π°ΠΏΠΎΠΌΠΈΠ½Π°Π½ΠΈΠ΅?', reply_markup=key_reply_reminder(),
    #                        reply_to_message_id=update.message.message_id)

def f_files(update, context):
    bot.send_audio(chat_id=update.message.chat.id, audio=open('tests/test.mp3', 'rb'))
    bot.send_document(update.message.chat.id, document=open('tests/test.zip', 'rb'))
    file_id = update.message.voice.file_id
    file = update.message.photo[-1]
    newFile = bot.get_file(file_id)
    newFile.download('voice.ogg')
    # path = file.download("1.jpg")
    # context.bot.send_message(update.message.chat.id, text='ΠΠΎΡΠ»Π°ΡΡ Π½Π° ΠΏΠΎΡΡΡ?', reply_markup=key_reply_media())

def f_send_data(update, context):
    from_user = update.message.from_user
    from_user_id = update.message.from_user.id
    from_user_username = update.message.from_user.username
    try:
        context.bot.send_message(TG_SOLSUPERGROUP_ID, text=f'ΠΠΎΠ²ΡΠ΅ Π΄Π°Π½Π½ΡΠ΅ ΠΏΠΎΠ»ΡΡΠ΅Π½Ρ:\n'\
                                                     f'1. USER: {from_user}\n' \
                                                     f'2. ID: {from_user_id}\n' \
                                                     f'3. USERNAME: {from_user_username}', reply_markup=key_reply_main1())
    except Exception as e:
        print(e)
    context.bot.send_message(TG_SOL_ID, text=f'ΠΠΎΠ²ΡΠ΅ Π΄Π°Π½Π½ΡΠ΅ ΠΏΠΎΠ»ΡΡΠ΅Π½Ρ:\n'\
                                                     f'1. USER: {from_user}\n' \
                                                     f'2. ID: {from_user_id}\n' \
                                                     f'3. USERNAME: {from_user_username}', reply_markup=key_reply_main1())

def f_callbackbutton(update, context):
    query = update.callback_query
    print(f' query: {query}')
    query.answer()
    callback_data = query.data
    print(f' callback_data: {callback_data}')
    query.edit_message_text(text=f"ΠΡΠ±ΡΠ°Π½Π½ΡΠΉ Π²Π°ΡΠΈΠ°Π½Ρ: {callback_data}")

def f_all(update, context):
    print(f' NA: {update.message}')
    context.bot.send_message(update.message.chat.id, text="β ΠΠ°Π½Π½ΡΠΉ Π²ΠΈΠ΄ ΡΠΎΠΎΠ±ΡΠ΅Π½ΠΈΠΉ ΠΏΠΎΠΊΠ° Π½Π΅ ΠΎΠ±ΡΠ°Π±Π°ΡΡΠ²Π°Π΅ΡΡΡ", reply_markup=key_reply_start())

def f_error(update, context):
    try:
        raise context.error
    except Unauthorized as e:
        print(f'Update {update} caused error: {e}')
    except BadRequest as e:
        print(f'Update {update} caused error: {e}')
    except TimedOut as e:
        print(f'Update {update} caused error: {e}')
    except NetworkError as e:
        print(f'Update {update} caused error: {e}')
    except ChatMigrated as e:
        print(f'Update {update} caused error: {e}')
    except TelegramError as e:
        print(f'Update {update} caused error: {e}')

############################# Handlers #########################################

def main():

    updater = Updater(TOKEN, use_context=True)
    bot = updater.dispatcher


    bot.add_handler(CommandHandler(['s'], f_start))
    bot.add_handler(CommandHandler(['start'], f_start))
    bot.add_handler(CommandHandler(['t'], f_test))
    bot.add_handler(CommandHandler(['help', 'h'], f_faq))


    bot.add_handler(
        MessageHandler(
            Filters.regex('π MENU') | Filters.regex('β ΠΠ΅ Π½Π°Π΄ΠΎ')
            | Filters.regex('β ΠΠ΅Ρ') | Filters.regex('π ΠΠ΅ΡΠ½ΡΡΡΡΡ Π² ΠΌΠ΅Π½Ρ')
            | Filters.regex('β Cancel'), f_main))
    bot.add_handler(MessageHandler(Filters.regex('β FAQ'), f_faq))
    bot.add_handler(MessageHandler(Filters.regex('π ΠΠ°Π·Π°Π΄'), f_start))
    bot.add_handler(MessageHandler(Filters.regex('TEST'), f_test))
    bot.add_handler(MessageHandler(Filters.regex('π My Data'), f_mydata))

    bot.add_handler(MessageHandler(
                Filters.regex('https://www.youtube.com')
                | Filters.regex('https://youtu.be')
                | Filters.regex('https://youtube.com'), f_yt1))



    bot.add_handler(
        MessageHandler(
            Filters.regex('π€ ΠΡΠΊΠ»ΡΡΠΈΡΡ ΡΠ°ΡΠ±ΠΎΡΠ°')
            | Filters.regex('π€ Talk to Chatbot'), f_talk_dialogflow_onoff))




    conversation_handler_translate = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('πΊπΈ-π·πΊ Translate') | Filters.regex('β© ΠΠ΅ΡΠ΅Π²Π΅ΡΡΠΈ Π΅ΡΡ?'), f_translate_start)
        ],
        states={
            "INPUTTEXT": [MessageHandler(Filters.regex('^(πΊπΈEN->RUπ·πΊ|π·πΊRU->ENπΊπΈ)$'), f_translate_ln)],
            "ENRU": [MessageHandler(Filters.text & ~Filters.command, f_translate_enru)],
            "RUEN": [MessageHandler(Filters.text & ~Filters.command, f_translate_ruen)]
        },
        fallbacks=[
            MessageHandler(Filters.regex('β ΠΡΠΌΠ΅Π½Π°') | Filters.regex('β ΠΠ΅Ρ'), f_translate_cancel)
        ]
    )

    conversation_handler_task = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('β° Add note'), f_task_start)
        ],
        states={
            "STEP1": [MessageHandler(Filters.text, f_task1)],
            "STEP2": [MessageHandler(Filters.text, f_task2)],
            "STEP3": [MessageHandler(Filters.text, f_task3)],
        },
        fallbacks=[
            MessageHandler(Filters.regex('β Cancel'), f_task_cancel),
            MessageHandler(Filters.regex('π Back'), f_task2)
        ]
    )

    conversation_handler_stt = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('π STT&TTS') | Filters.regex('β© Π‘ΠΊΠΎΠ½Π²Π΅ΡΡΠΈΡΠΎΠ²Π°ΡΡ Π΅ΡΡ'), f_tts_start)
        ],
        states={
            "STEP1": [
                # MessageHandler(Filters.text, f_tts1),
                MessageHandler(Filters.regex('πΆSPEECH TO πTEXT') | Filters.regex('πTEXT TO πΆSPEECH'), f_tts1)
            ],
            "STEP2": [
                MessageHandler(Filters.text, f_tts2),
                MessageHandler(Filters.voice, f_tts3),
                MessageHandler(Filters.document | Filters.photo | Filters.audio, f_tts_wrong)
            ],
            "STEP3": [
                MessageHandler(Filters.text, f_tts4)
            ],
        },
        fallbacks=[
            MessageHandler(Filters.regex('β ΠΡΠΌΠ΅Π½Π°') | Filters.regex('β ΠΠ΅Ρ'), f_tts_cancel)
        ]
    )


    bot.add_handler(conversation_handler_task)
    bot.add_handler(conversation_handler_stt)
    bot.add_handler(conversation_handler_translate)



    bot.add_handler(MessageHandler(Filters.video | Filters.audio | Filters.voice | Filters.document | Filters.photo, f_other))
    bot.add_handler(MessageHandler(Filters.forwarded | Filters.caption, f_other))
    bot.add_handler(MessageHandler(Filters.text, f_text))
    bot.add_handler(CallbackQueryHandler(f_callbackbutton))
    bot.add_handler(MessageHandler(Filters.all, f_all))
    updater.dispatcher.add_error_handler(f_error)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url="https://tgsolbot.herokuapp.com/" + TOKEN)
    updater.idle()

if __name__ == '__main__':
    main()
