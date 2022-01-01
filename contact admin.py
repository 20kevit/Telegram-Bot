import logging
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

# Enable logging:
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

updater = Updater('BOT TOKEN') #get your own bot token from t.me/botfather
dp = updater.dispatcher 

#-------------------------------------------------------------------------------

def start(update, context):
    #some text that will be sent to user when hits the start command:
    txt_reply = "Wellcome !"
    update.message.reply_text(txt_reply)

#calling "start" function when user send /start command:
start_handler = CommandHandler("start", start) 

#add this handler to bot:
dp.add_handler(start_handler)

#-------------------------------------------------------------------------------

#admin's nummerical id:
admin_id = 123456789
def messaging(update, context):
    try:
        #forward message from user to admin:
        context.bot.forward_message(
            chat_id = admin_id,
            from_chat_id = update.message.chat_id,
            message_id = update.message.message_id
        )

        #tell user if message sent
        update.message.reply_text("yoru message sent successfully \U00002705")

    #if there is a problem:
    except Exception as error:
        #tell user that ther is a problem:
        update.message.reply_text("error!")

        #send a message to admin that contain some information about error:
        context.bot.send_message(
            chat_id = admin_id,
            text = str(error)
        )

# *Filters.all* tells handler that it should respond to all messages (except /start command that added before)
message_handler = MessageHandler(Filters.all, messaging)

#add this handler to bot:
dp.add_handler(message_handler)

#-------------------------------------------------------------------------------

#start the bot:
updater.start_polling()

#for stop:
updater.idle()
