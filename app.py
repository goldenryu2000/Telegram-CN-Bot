import logging
from telegram.ext import Updater ,CommandHandler,MessageHandler,Filters,Dispatcher
from flask import Flask , request
from telegram import Bot ,Update ,ReplyKeyboardMarkup
#Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" , level = logging.INFO)
logger = logging.getLogger(__name__)

#Create Updater
TOKEN = "1309642095:AAGJoUnWhHvKmMVp1ddYItF3H8TQDI1abqE"

app = Flask(__name__)

@app.route('/') #creating a sample route
def index():
	return "Hello!"

@app.route(f'/{TOKEN}'  , methods = ['GET' , 'POST'])
def webhook():
	#########Webhook view which receives updates from telegram######
	#create update object from json.format request data
	update  =Update.de_json(request.get_json() , bot)
	#process update
	dp.process_update(update)
	return "ok"

####### DailogFlow Integration
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client.json"

import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "news-bot-vwmepp"

def detect_intent_from_text(text,session_id,language_code='en'):
	session = dialogflow_session_client.session_path(PROJECT_ID,session_id)
	text_input  =dialogflow.types.TextInput(text = text , language_code = language_code)
	query_input = dialogflow.types.QueryInput(text = text_input)
	response = dialogflow_session_client.detect_intent(session = session,query_input = query_input)
	return response.query_result

def get_reply(query,chat_id):
	response = detect_intent_from_text(query,chat_id)

	if response.intent.display_name =='iGet_news':
		return "get_news",dict(response.parameters)
	else:
		return "small_talk",response.fulfillment_text

from gnewsclient import gnewsclient
client = gnewsclient.NewsClient()

def fetch_news(parameters):
	client.language = parameters.get('language')
	client.location = parameters.get('geo-country')
	client.topic = parameters.get('topic')

	return client.get_news()[:5]#for first five articles


######################################
topics_keyboard = [
['Top Stories' ,'World' , 'Nation'],
['Buisness' , 'Technology' , 'Entertainment'],  #Keyboard for keyboard markup
['Sports' , 'Science' , 'Health']
]


def news(bot,update):
	bot.send_message(chat_id = update.message.chat_id , text = 'Choose a Category',
		reply_markup = ReplyKeyboardMarkup(keyboard = topics_keyboard , one_time_keyboard = True))


def start(bot,update): #start Function
	print(update)
	author = update.message.from_user.first_name #to get the first name of who has send the command
	msg = update.message.text
	reply = "Hi! {}".format(author)
	bot.send_message(chat_id = update.message.chat_id , text =reply)

def reply_text(bot,update):
	intent,reply = get_reply(update.message.text , update.message.chat_id)
	if intent=="get_news":
		articles= fetch_news(reply)
		for article in articles:
			bot.send_message(chat_id = update.message.chat_id , text =article['link'])
	else:
		bot.send_message(chat_id = update.message.chat_id , text =reply) #chat_id tells which caht to send message to

def echo_sticker(bot,update):
	context.bot.send_sticker(chat_id = update.message.chat_id,sticker=update.message.sticker.file_id)

def  _help(bot,update):
	help_txt = "This is a help text"
	bot.send_message(chat_id = update.message.chat_id , text =help_txt)	

def error(update):
    logger.warning('Update "%s" caused error "%s"', update, update.error)


bot = Bot(TOKEN)
try:
	bot.set_webhook("https://5039ef65306d.ngrok.io/"+TOKEN)
except Exception as e:
	print(e)
dp = Dispatcher(bot, None) #creating a dispatcher for the updater which will dispatch the updater
#adding Dispatching Handlers
dp.add_handler(CommandHandler("start" , start)) #handling commands
dp.add_handler(CommandHandler("help" , _help))
dp.add_handler(CommandHandler("news" , news))
dp.add_handler(MessageHandler(Filters.text , reply_text))
dp.add_handler(MessageHandler(Filters.sticker , echo_sticker))
dp.add_error_handler(error)	


if __name__ =="__main__":
	app.run(port = 8443)

