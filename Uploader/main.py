#this is a bot that get a file(video, audio, photo, etc) and give a link
#everyone can get the file with that link if file is public

import logging
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence, ConversationHandler
from random import choice

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

persistence = PicklePersistence(filename='database')
updater = Updater("BOT TOKEN", persistence=persistence) 
dp = updater.dispatcher

#------------------------------------------------------------------------------------------------------
def start(update, context):
    #default setting:
    if(not "setting" in context.user_data):
        setting = {
            "public": True,
            "timer": 0
        }
        context.user_data["setting"] = setting
        
    #normal start:
    if(not context.args):
        update.message.reply_text("send some files, so i will send you a link to acsess file later:")

    #starting by a given link with payloads(file name)
    else:
        file_name = context.args[0]
        #defined function:
        send_file(update, context, file_name)

#------------------------------------------------------------------------------------------------------
def send_file(update, context, file_name):
    # 'm' treats like a shortcut for 'update.message'
    m = update.message
    
    #public files:
    if(file_name in context.bot_data):
        source = context.bot_data
    
    #private files:
    elif(file_name in context.user_data):
        source = context.user_data

    #invalid links contain invalid file_names:
    else:
        m.reply_text("File Not Found")
        return
    
    #file founded:
    source[file_name]["downloads"] += 1
    downloads = source[file_name]["downloads"]
    file_type = source[file_name]["type"]
    file_id = source[file_name]["file_id"]
    caption = source[file_name]["caption"]
    timer = source[file_name]["timer"]

    #call suitable function for each type of file:
    functions = {
        "video": m.reply_video,
        "animation": m.reply_animation,
        "voice": m.reply_voice,
        "audio":  m.reply_audio,
        "document": m.reply_document,
        "videoNote": m.reply_video_note,
        "photo": m.reply_photo
    }
    message = functions[file_type](file_id, caption=caption)
    
    #how many times this media downloaded:
    m.reply_text(f"downloads: {downloads}")
    
    if(timer > 0):
    	context.job_queue.run_once(distroy, timer, context={"chat":message.chat_id, "message":message.message_id})
    
def distroy(context):
    data = context.job.context
    chat_id = data["chat"]
    message_id = data["message"]
    context.bot.delete_message(chat_id, message_id)

#------------------------------------------------------------------------------------------------------
#creating a list of allowed characters for generating 'file_names'
char_list = [chr(i) for i in range(48,58)] + [chr(i) for i in range(65,91)] + [chr(i) for i in range(97,123)] #contains: a-z, A-Z, 0-9

#a function for generate random string:
def rand_string(inp_list, n):
    result = ''
    for i in range(n):
        result += choice(char_list)

    #if generated name is duplicated:
    if(result in inp_list):
        return rand_string(inp_list, n)
    else:
        return result

#supported file types:
file_types = {
    telegram.files.video.Video : "video",
    telegram.files.animation.Animation : "animation",
    telegram.files.voice.Voice : "voice",
    telegram.files.audio.Audio : "audio",
    telegram.files.document.Document : "document",
    telegram.files.videonote.VideoNote : "videoNote",
    telegram.files.photosize.PhotoSize : "photo"
}
#------------------------------------------------------------------------------------------------------
def get_file(update, context):
    # 'm' treats like a shortcut for 'update.message'
    m = update.message
    
    #attachment can be a video, voice or etc.
    attachment = update.message.effective_attachment

    file_name = rand_string(context.bot_data, 8)

    bot_username = 'example_bot' #without @
    link = f"t.me/{bot_username}?start={file_name}"

    #for 'photo' files attachment is a list of photos with different sizes:
    if(type(attachment) == list):
        attachment = attachment[-1]
        
    if(not type(attachment) in file_types):
        m.reply_text("File Format not Supported")
        return
		
    setting = context.user_data["setting"]
    is_public = setting["public"]
    timer = setting["timer"]

    file_type = file_types[type(attachment)]
    file_id = attachment.file_id
    caption = m.caption
	
	if(is_public):
    		context.bot_data[file_name] = {"type":file_type, "file_id":file_id, "caption":caption, "timer":timer, "downloads":0}
	else:
    		context.user_data[file_name] = {"type":file_type, "file_id":file_id, "caption":caption, "timer":timer, "downloads":0}
    
    #send link to user:
    m.reply_text("Here you are:")
    m.reply_text(link)

#------------------------------------------------------------------------------------------------------
#define some states for handling conversation:	
stt_choose, stt_change_timer = range(2)

#this function ends covnersation:
def cancel(update, context):
	update.message.reply_text('send your files:', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

#calls the cancel function when user sends a command or 'end' message or non-text message:
cancel_handler = MessageHandler(Filters.command | Filters.regex("^end$") | ~Filters.text, cancel)

#execute when user send /setting command:
def change_setting(update, context):
	#get current setting:	
    setting = context.user_data["setting"]
    timer = setting["timer"]
    is_public = setting["public"]
	
	
	#show user current setting:
    txt_reply = "your current setting:\ntype: "
    txt_reply += "public" if is_public else "private"
    txt_reply += "\ntimer: "
    txt_reply += str(timer) if (timer > 0) else "not set"
    update.message.reply_text(txt_reply)
	
	#options:
    keyboard = ReplyKeyboardMarkup(
        [["change type", "reset timer"], ["end"]],
        one_time_keyboard = True,
        resize_keyboard = True
    )
    update.message.reply_text("choose:", reply_markup=keyboard)
    return stt_choose

#execute when user choose an option:
def choose(update, context):
    message = update.message.text
	

    if(message == "change type"):
		#inverting public/private situation:
        value = context.user_data["setting"]["public"]
        context.user_data["setting"]["public"] = not value
        update.message.reply_text("done")
        return change_setting(update, context)

    elif(message == "reset timer"):
        keyboard = ReplyKeyboardMarkup(
            [["end"]],
            one_time_keyboard = True,
            resize_keyboard = True
        )
        update.message.reply_text(
            "send new value for timer:\n(0 for disable)",
            reply_markup=keyboard
        )
        return stt_change_timer

    else:
        update.message.reply_text("invalid input")
        return stt_choose

#set timer to given value:
def change_timer(update, context):
    m = update.message
    timer = m.text
	
    try:
        timer = int(timer)
        if(timer < 0):
            m.reply_text("please send an non-negative integer")
            return stt_change_timer

        else:
            context.user_data["setting"]["timer"] = timer
            update.message.reply_text("done")
            return change_setting(update, context)

    except:
        m.reply_text("please send an non-negative integer")
        return stt_change_timer

conversation_setting = ConversationHandler(
    entry_points = [CommandHandler("setting", change_setting)],
    states = {
        stt_choose : [
            cancel_handler,
            MessageHandler(Filters.text, choose)
        ],
        stt_change_timer : [
            cancel_handler,
            MessageHandler(Filters.text, change_timer)
        ]
    },
    fallbacks = [cancel_handler],
    name="my_login_conversation",
    persistent=True,
)

#------------------------------------------------------------------------------------------------------
#adding handlers:
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(~Filters.text, get_file))
dp.add_handler(conversation_setting)

#start bot:
updater.start_polling()

#for stop:
updater.idle()
