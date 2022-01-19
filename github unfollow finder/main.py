import logging
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from requests import get
from bs4 import BeautifulSoup

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

updater = Updater("BOT TOKEN") 
dp = updater.dispatcher


#returns a list of usernames:
#returns an empty list for bad inputs:
def find(user_name, tab="followers"):
    results = []
    page_num = 1
    while(True):
        url = f"https://github.com/{user_name}?page={page_num}&tab={tab}"
        page = get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        #each user is in a div element with this class:
        elements = soup.find_all(class_="d-inline-block no-underline mb-1")

        #if this is last page(empty):
        if(not elements):
            break

        #each element has 2 span element that the second one contains user's id:
        for element in elements:
            name = element.find_all("span")[1].text
            results.append(name)

        #next_page:
        page_num += 1

    return results

def start(update, context):
    update.message.reply_text("wellcom!\n\nsend your github username:")
    
dp.add_handler(CommandHandler("start", start))
    
def answer(update, context):
    m = update.message
    
    #tell user that bot is working:
    m.reply_text("working ...")
	
	#github username
    username = m.text
    
    followers = find(username)
    following = find(username, "following")
    
	#count of followers and followings
    m.reply_text(f"followers: {len(followers)}\nfollowing: {len(following)}\n")
    
    unfollowers = [person for person in following if(not person in followers)]
    txt_reply = "people who didn't followed back:"
    for person in unfollowers:
        txt_reply += f"\n- [{person}](https://github.com/{person})"
    m.reply_text(txt_reply, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    fans = [person for person in followers if(not person in following)]
    txt_reply = "people followed you, but you didn't follow back:"
    for person in fans:
        txt_reply += f"\n- [{person}](https://github.com/{person})"
    m.reply_text(txt_reply, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    
    print(str(update.effective_user.id), " -> ", str(m.text))
    
dp.add_handler(MessageHandler(Filters.text, answer))

updater.start_polling()
updater.idle()
