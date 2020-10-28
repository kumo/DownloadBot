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


def download_media(link, folder_name):

    # Use you_get to download the file to the specified folder
    # if it fails it will return an error (check=True)
    # which we pass to the calling function
    subprocess.run(
        [YOU_GET_APP, "--output-dir={}".format(folder_name), link], check=True
    )


def log_error(message):
    with open(LOG_FILE, "a") as myfile:
        myfile.write(message)
        myfile.write("\n")
        
    logger.warning(message)


def parse_message(update, context):

    download_link = update.message.text
    folder_name = time.strftime("%Y%m%d-%H%M%S")

    bot_message = update.message.reply_text("Downloading media...")
        
    try:
        # Try to download the media. If there is a problem,
        # an exception is raised.
        download_media(download_link, folder_name)

        bot_message.edit_text("Media downloaded.")
    except Exception as e:
        print(e)
        bot_message.edit_text("Couldn't download the media, but I have taken note.")
        log_error("Couldn't download link: {}".format(download_link))

        # We can't do anything else, so let's leave the function
        return

    # Inform the user that we are sending something
    bot_message = update.message.reply_text("Sending media...")

    try:
        # Try to send the media. If there is a problem,
        # an exception is raised.
        send_media(folder_name, update.message)

        bot_message.edit_text("Media sent.")
    except Exception as e:
        print(e)
        bot_message.edit_text("Couldn't send the media, but I have taken note.")

        log_error("Couldn't send media in {} for {}".format(folder_name, download_link))


def send_media(folder_name, message):
    files = [f for f in listdir(folder_name) if isfile(join(folder_name, f))]

    # Ensure that there are files
    assert(len(files) > 0)

    for file in files:
        filename = join(folder_name, file)
        message.reply_document(document=open(filename, 'rb'), timeout=TIMEOUT)



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
