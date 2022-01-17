#this is a bot that get a file(video, audio, photo, etc) and give a link
#everyone can get the file with that link

import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from random import choice

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

updater = Updater("BOT TOKEN") 
dp = updater.dispatcher

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
    
    if(timer > 0)
    	context.job_queue.run_once(distroy, timer, context={"chat":message.chat_id, "message":message.message_id})
    
def distroy(context):
    data = context.job.context
    chat_id = data["chat"]
    message_id = data["message"]
    context.bot.delete_message(chat_id, message_id)

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

#adding handlers:
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(~Filters.text, get_file))

#start bot:
updater.start_polling()

#for stop:
updater.idle()
