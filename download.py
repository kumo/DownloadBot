#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple Bot to download (Twitter) videos and send them back.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

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
TIMEOUT=360 # How much time do we want to wait (in seconds) before giving up?
BOT_TOKEN="***REMOVED***"

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


# Download the media to the specified folder
def download_media(link, folder_name):
    # Use 'you_get' to download the file to the specified folder
    # if it fails it will return an exception/error (check=True).
    # Since we don't catch the exception here, it will be passed
    # to the calling function (parse_media)
    subprocess.run(
        [YOU_GET_APP, "--output-dir={}".format(folder_name), link], check=True
    )

# Save error messages to a file and print them to the console
def log_error(message):
    with open(LOG_FILE, "a") as myfile:
        myfile.write(message)
        myfile.write("\n")
    
    # Use the logger to print the information in the console
    logger.warning(message)


# This function tries to download the media from the link,
# and then send it back to the user, keeping them informed
def parse_message(update, context):
  	# Use the text from the message as the download link
    download_link = update.message.text
    
    # We want to save the media to a specific folder:
    # Year-Month-Day-Hour-Minutes-Seconds
    folder_name = time.strftime("%Y%m%d-%H%M%S")

    # Inform the user that we are downloading something.
    # We store the message so that we can edit it afterwards
    bot_message = update.message.reply_text("Downloading media...")
    
    # Try to download the media. If there is a problem,
    # an exception/error is raised. If we don't catch the exception,
    # the app will quit, but we want to tell the user and continue
    try:
      	# Download the media in the link to the specified folder
        # It will raise an exception if there is a problem.
        download_media(download_link, folder_name)

        # Update the previous message to tell the user that we have finished
        bot_message.edit_text("Media downloaded.")
    except Exception as e:
        # Update the previous message to tell the user that something went wrong
        bot_message.edit_text("Couldn't download the media, but I have taken note.")
        # Log the problem
        log_error("Couldn't download link: {}".format(download_link))

        # We can't do anything else, so let's leave the function
        return

    # Inform the user that we are sending something
    # We store the message so that we can edit it afterwards
    bot_message = update.message.reply_text("Sending media...")

    # Try to send the media. If there is a problem,
    # an exception is raised.
    try:
      	# Send the media in the link to the specified folder
        # as a reply to the message
        # It will raise an exception if there is a problem.
        send_media(folder_name, update.message)

        # Update the previous message to tell the user that we have finished
        bot_message.edit_text("Media sent.")
    except Exception as e:
        # Update the previous message to tell the user that something went wrong
        bot_message.edit_text("Couldn't send the media, but I have taken note.")
        # Log the problem
        log_error("Couldn't send media in {} for {}".format(folder_name, download_link))


# This function sends the media in the specified folder as a reply
def send_media(folder_name, message):
  	# Collect all the files in the folder and skip the folders
    files = [f for f in listdir(folder_name) if isfile(join(folder_name, f))]

    # Ensure that there are files. This should raise an exception otherwise.
    assert(len(files) > 0)

    for file in files:
      	# We have a folder name and a file name, so combine them together
        filename = join(folder_name, file)
        # Send the document as a reply to the message. The timeout is specified
        # otherwise it might fail after trying for 20 seconds
        message.reply_document(document=open(filename, 'rb'), timeout=TIMEOUT)


def main():
    # Start the bot
    updater = Updater(BOT_TOKEN, use_context=True)

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
