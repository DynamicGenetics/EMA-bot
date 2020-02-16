import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import pandas as pd
import datetime
import logging


#Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

#This is used in the conversationHandler
logger = logging.getLogger(__name__)

#Initiate bot object
bot = telegram.Bot(token='1071227516:AAGrMoQk-dZ9rwj0H_PqYX1FeC3TDqhr76s')

###############
## FUNCTIONS ##
###############

#Function that defines what the bot should do on receiving the \start message 
def start(update, context):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Welcome to the University of Bristol's Mood Music Study! " "Thanks so much for taking part. " "Please remember to enable push notifications from Telegram, and when that is done reply /ready.")

#Function that will run the EMA survey at the times we want every day. 
def daily_job(update, job_queue):
    """ Running on Mon, Tue, Wed, Thu, Fri, Sat, Sun = tuple(range(7)) """
    bot.send_message(chat_id=update.message.chat_id, text="Great, you\'re all set up! " "You will receive a message when it\'s time for your next survey. If you don\'t want to wait you can try in out now by replying /ema. " "Have a good day :)")
    t = datetime.time(20, 16, 00, 000000)
    job_queue.run_daily(ema_survey, t, days=tuple(range(7)), context=update)

#Function to manage unrecognised commands
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command")


#Initialise the states for conversation handler - NameError saying they aren't defined otherwise 
HAPPINESS, ENERGY, DONE = range(3)

def ema_start(update, context):
    kb = [['1','2', '3', '4', '5'], ['6', '7', '8', '9', '10']]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True)

    update.message.reply_text(
        "Hi, it\'s time for another survey. "
        "How happy do you feel right now, where 1 = Very Unhappy and 10 = Very Happy?",
        reply_markup=kb_markup)

    #Add the chat ID, the time stamp of the reply and the message text to the dataframe
    #df.loc[len(df)] = [update.message.chat_id, update.message.date, update.message.text]

    return HAPPINESS

def ema_happiness(update, context):
    user = update.message.from_user
    logger.info("Happiness of %s: %s", user.username, update.message.text)

    kb = [['1','2', '3', '4', '5'], ['6', '7', '8', '9', '10']]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, one_time_keyboard=True)

    update.message.reply_text(
        "How energetic do you feel right now, where 1 = Very Lethargic and 10 = Very Energetic?",
        reply_markup=kb_markup)
    #Add the chat ID, the time stamp of the reply and the message text to the dataframe
    #df.loc[len(df)] = [update.message.chat_id, update.message.date, update.message.text]
    return ENERGY

def ema_energy(update, context):
    user = update.message.from_user
    logger.info("Energy of %s: %s", user.username, update.message.text)
    update.message.reply_text("Thank you! All done.")

    return ConversationHandler.END


#######################
## MAIN METHOD STUFF ##
#######################

def main():
    updater = Updater(token='1071227516:AAGrMoQk-dZ9rwj0H_PqYX1FeC3TDqhr76s', use_context=True)

    dispatcher = updater.dispatcher

    #Initialise dataframe to store survey responses in.
    #df = pd.DataFrame(columns=['chat_id', 'timestamp', 'reply'])

    #j = updater.job_queue

    ##########################
    ## CONVERSATION HANDLER ##
    ##########################

    ema_handler = ConversationHandler(
        entry_points=[CommandHandler('ema', ema_start)],

        states={
            HAPPINESS: [MessageHandler(Filters.regex('[0-9]|10'), ema_happiness)],

            ENERGY: [MessageHandler(Filters.regex('[0-9]|10'), ema_energy)]
        },

        fallbacks = []
    )

    ####################
    ## OTHER HANDLERS ##
    ####################

    #Conversation Handler
    dispatcher.add_handler(ema_handler)

    #Ready Handler which sets up the JoQueue
    ready_handler = CommandHandler('ready', daily_job, pass_job_queue=True)
    dispatcher.add_handler(ready_handler)

    #Start Handler - responds to the \start message using the start function. 
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    #Unknown Handler - 
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    #Set Bot running
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()