import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import datetime
import logging, csv, io, os, sys

#Credentials file 
from credentials import bot_creds

############
## SET-UP ##
############

#Initiate bot object
bot = telegram.Bot(token=bot_creds)

#Setting up logging
#Generate log name with path based on cwd of this Python script
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

#Instatiate logger
logger = logging.getLogger(__name__)

log_fname = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'ema_log.csv')
fh = logging.FileHandler(log_fname)
fh.setLevel(logging.INFO)
logger.addHandler(fh)

###############
## FUNCTIONS ##
###############

#Function that defines what the bot should do on receiving the \start message 
def start(update, context):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Welcome to the University of Bristol's Mood Music Study! " "Thanks so much for taking part. " "Please remember to enable push notifications from Telegram, and when that is done reply /ready.")

def daily_message(context: telegram.ext.CallbackContext):
     context.bot.send_message(chat_id=context.job.context, text='This is a sheduled message')

def callback_daily(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Setting up your daily surveys!")
    t = datetime.time(14, 29, 00, 000000)
    context.job_queue.run_daily(daily_message, t, context=update.message.chat_id)

#Function that will run the EMA survey at the times we want every day. 
# def daily_job(update, job_queue):
#     """ Running on Mon, Tue, Wed, Thu, Fri, Sat, Sun = tuple(range(7)) """
#     bot.send_message(chat_id=update.message.chat_id, text="Great, you\'re all set up! " "You will receive a message when it\'s time for your next survey. If you don\'t want to wait you can try it out now by replying /ema. " "Have a good day :)")
#     t = datetime.time(20, 16, 00, 000000)
#     job_queue.run_daily(ema_survey, t, days=tuple(range(7)), context=job.context)

#Function to manage unrecognised commands
def unknowncommand(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command")

#Function to manage unrecognised commands
def unknowntext(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I\'m not able to understand what you have said. Please see /help for an overview of my commands, or wait until your next survey. Thank you!")

#Function to manage unrecognised commands
def helpme(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Soon this will show you all my available commands!")


#Initialise the states for conversation handler - NameError saying they aren't defined otherwise 
HAPPINESS, ENERGY, DONE = range(3)

def ema_start(update, context):

    #Custom keyboard layout
    kb = [['1','2', '3', '4', '5'], ['6', '7', '8', '9', '10']]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True)

    update.message.reply_text(
        "Hi, it\'s time for another survey. "
        "How happy do you feel right now, where 1 = Very Unhappy and 10 = Very Happy?",
        reply_markup=kb_markup)

    return HAPPINESS

def ema_happiness(update, context):
    user = update.message.from_user
    
    #Logs:      username,      chat id,               datetime of original message, question, datetime of reply,  reply info
    logger.info("%s, %s, %s, Happiness, %s, %s", user.username, update.message.chat_id, update.message.forward_date, update.message.date, update.message.text)

    #Custom keyboard layout
    kb = [['1','2', '3', '4', '5'], ['6', '7', '8', '9', '10']]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True)

    update.message.reply_text(
        "How energetic do you feel right now, where 1 = Very Lethargic and 10 = Very Energetic?",
        reply_markup=kb_markup)

    return ENERGY

def ema_energy(update, context):
    user = update.message.from_user
    #Logs:      username,      chat id,               datetime of original message, question, datetime of reply,  reply info
    logger.info("%s, %s, %s, Energy, %s, %s", user.username, update.message.chat_id, update.message.forward_date, update.message.date, update.message.text)
    update.message.reply_text("Thank you! All done.")

    return ConversationHandler.END


#######################
## MAIN METHOD STUFF ##
#######################

def main():
    updater = Updater(token=bot_creds, use_context=True)

    dispatcher = updater.dispatcher

    job_queue = updater.job_queue

    ##########################
    ## CONVERSATION HANDLER ##
    ##########################

    ema_handler = ConversationHandler(
        entry_points=[CommandHandler('ema', ema_start)],

        states={
            HAPPINESS: [MessageHandler(Filters.regex('[1-9]|10'), ema_happiness)],

            ENERGY: [MessageHandler(Filters.regex('[1-9]|10'), ema_energy)]
        },

        fallbacks = []
    )

    ####################
    ## OTHER HANDLERS ##
    ####################

    #Conversation Handler
    dispatcher.add_handler(ema_handler)

    #Ready Handler which sets up the JoQueue
    dispatcher.add_handler(CommandHandler('ready', callback_daily, pass_job_queue=True))

    #Start Handler - responds to the \start message using the start function. 
    dispatcher.add_handler(CommandHandler('start', start))

    ##Help Command Handler - 
    dispatcher.add_handler(CommandHandler('help', helpme))

    #Unknown Command Handler - 
    dispatcher.add_handler(MessageHandler(Filters.command, unknowncommand))

    #Unknown Anything Handler - 
    dispatcher.add_handler(MessageHandler(Filters.text, unknowntext))

    #Set Bot running
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()