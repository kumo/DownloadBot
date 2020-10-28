#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple Bot to download (Twitter) videos and send them back.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatAction

# We need to be able to call an external app
import subprocess
import sys

# We need to be able to get today's date and current time
import time

# We need to be able to create folders and list contents of folders
from os import listdir
from os.path import isfile, join

import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

LOG_FILE="log.txt"
YOU_GET_APP="/usr/local/bin/you-get"
TIMEOUT=360

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def errors_command(update, context):
    """List all the download errors when the command /errors is issued."""
   
    # Open the log file in read mode 
    with open(LOG_FILE, "r") as myfile:
        # Get the text from the file
        text = myfile.read()

    # Send the contents of the file to the chat
    update.message.reply_text(text)


def download_media(link):

    result = subprocess.run(
        [YOU_GET_APP, "-i", link], capture_output=True, text=True, check=True
    )

    # print("stdout:", result.stdout)
    # print("stderr:", result.stderr)

    if "mp4" in result.stdout:
        # print("Contains a video")

        timestr = time.strftime("%Y%m%d-%H%M%S")
        # print(timestr)

        result = subprocess.run(
            # ["/usr/local/bin/you-get", "--output-filename=testing", link], capture_output=True, text=True, check=True
            [YOU_GET_APP, "--output-dir={}".format(timestr), link], capture_output=True, text=True, check=True
        )

        # print("Downloaded video")

        return timestr

        # update.send_document(chat_id=update.message.chat_id, document=open('test.mp4', 'rb'))
        # update.message.reply_document(document=open('testing.mp4', 'rb'))
        # document='test.mp4')
        # bot.send_document(chat_id=chat_id, document=open('test.mp4', 'rb')) 

def log_error(message):
    with open(LOG_FILE, "a") as myfile:
        myfile.write(message)


def parse_message(update, context):
    folder = ""
    link = ""
   
    #if "twitter" in update.message.text:
    #    link = update.message.text

    #if "tiktok" in update.message.text:
    #    link = update.message.text

    #if link == "":
    #    print("Couldn't find anything to download.")
    #    return

    update.message.reply_text("Trying to download media.")

    try:
        folder = download_media(update.message.text)
    
        update.message.reply_text("Media downloaded.")
    except Exception as e:
        # print(e)
        logger.warning("Couldn't download link: {}".format(update.message.text))
        update.message.reply_text("Couldn't download the link, but it has been logged")

        log_error("Error: {}\n".format(update.message.text))

        return

    # print("Should send contains of folder {}".format(folder))

    files = [f for f in listdir(folder) if isfile(join(folder, f))]
    # print(files)
    # print("There are {} files".format(len(files)))
    update.message.reply_text("There are {} file(s).".format(len(files)))

    filename = join(folder, files[0])

    try:
        update.message.reply_text("Trying to send file.")
        update.message.reply_document(document=open(filename, 'rb'), timeout=20)
        update.message.reply_text("Here is your file!")
    except Exception as e:
        print(e)
        logger.warning("Couldn't send file: {}".format(filename))
        update.message.reply_text("Couldn't send the file, trying again.")

        try:
            update.message.reply_document(document=open(filename, 'rb'), timeout=240)
            update.message.reply_text("Here is your file!")

        except Exception as e:
            logger.warning("Couldn't send file (again): {}".format(filename))
            update.message.reply_text("Couldn't send it. Logged and giving up.")
            log_error("Couldn't send file (again): {}".format(filename))

            return
        
        logger.warning("Managed to send file second time: {}".format(filename))
        log_error("Warning: took 2 times to send file: {}".format(filename))

def main():
    # Start the bot
    updater = Updater("***REMOVED***", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers for different commands (for example /start)
    # the string is the command (without "/") and after there is the function.
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("errors", errors_command))
    dp.add_handler(CommandHandler("help", help_command))

    # Add a handler for a normal message (in this case, parse_message)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, parse_message))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C.
    updater.idle()


if __name__ == '__main__':
    main()
