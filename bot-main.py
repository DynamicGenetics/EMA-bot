import telegram
import emoji
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import datetime
import logging, csv, io, os, sys

#Credentials file 
from credentials import bot_creds

############
## SET-UP ##
############

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
def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id,
                     text=emoji.emojize("Welcome to the University of Bristol's Mood Music Study! :musical_note: \nThanks so much for taking part. \nPlease remember to enable notifications from Telegram. \n\nYou will recieve a notification when it is time for you to answer a survey."))
   
    #context.job_queue.run_daily(ema_start, datetime.time(20, 35, 00, 000000), context=update.message.chat_id)
    context.job_queue.run_repeating(ema_start, interval=120, first=10, context=update.message.chat_id)

#Function for the /help command
def helpme(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Soon this will show you all my available commands!")

#Function to manage unrecognised commands
def unknowncommand(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn\'t understand that command")

#Function to manage text input
def unknowntext(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I\'m only able to understand your numeric survey answers. \nPlease email nina.dicara@bristol.ac.uk if you need anything, or wait until your next survey. \nThank you!")

#Initialise the states for conversation handler.
HAPPINESS, ENERGY = range(2)

def ema_start(context: telegram.ext.CallbackContext):

    #Custom keyboard layout
    kb = [['1','2', '3', '4', '5'], ['6', '7', '8', '9', '10']]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True)

    context.bot.send_message(chat_id=context.job.context, text = "Hi, it\'s time for another survey. \nHow happy do you feel right now, where 1 = Very Unhappy and 10 = Very Happy?",
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
        "How energetic do you feel right now, where 1 = Very Tired and 10 = Very Energetic?",
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

    #Initialise the updater and dispatcher for main method. 
    updater = Updater(token=bot_creds, use_context=True)
    dispatcher = updater.dispatcher

    ###########################
    ## CONVERSATION HANDLERS ##
    ###########################

    ema_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('[1-9]|10'), ema_happiness)],

        states={
            ENERGY: [MessageHandler(Filters.regex('[1-9]|10'), ema_energy)]
        },

        fallbacks = []
    )

    #EMA Conversation Handler
    dispatcher.add_handler(ema_handler)

    ######################
    ## COMMAND HANDLERS ##
    ######################

    #Start Handler which sets up the Job-Queue
    dispatcher.add_handler(CommandHandler('start', start, pass_job_queue=True))

    #Help Command Handler 
    dispatcher.add_handler(CommandHandler('help', helpme))

    ######################
    ## MESSAGE HANDLERS ##
    ######################

    #Unknown Command Handler - 
    dispatcher.add_handler(MessageHandler(Filters.command, unknowncommand))

    #Unknown Anything Handler - 
    dispatcher.add_handler(MessageHandler(Filters.text, unknowntext))

    #Set Bot running
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()