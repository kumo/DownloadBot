#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatAction

import subprocess
import sys

import time

from os import listdir
from os.path import isfile, join
# # Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


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
    
    with open("log.txt", "r") as myfile:
        text = myfile.read()

    update.message.reply_text(text)


def download_media(link):

    result = subprocess.run(
        ["/usr/local/bin/you-get", "-i", link], capture_output=True, text=True, check=True
    )

    # print("stdout:", result.stdout)
    # print("stderr:", result.stderr)

    if "mp4" in result.stdout:
        # print("Contains a video")

        timestr = time.strftime("%Y%m%d-%H%M%S")
        # print(timestr)

        result = subprocess.run(
            # ["/usr/local/bin/you-get", "--output-filename=testing", link], capture_output=True, text=True, check=True
            ["/usr/local/bin/you-get", "--output-dir={}".format(timestr), link], capture_output=True, text=True, check=True
        )

        # print("Downloaded video")

        return timestr

        # update.send_document(chat_id=update.message.chat_id, document=open('test.mp4', 'rb'))
        # update.message.reply_document(document=open('testing.mp4', 'rb'))
        # document='test.mp4')
        # bot.send_document(chat_id=chat_id, document=open('test.mp4', 'rb')) 

def log_error(message):
    with open("log.txt", "a") as myfile:
        myfile.write(message)


def parse(update, context):
    """Echo the user message."""
    folder = ""
    link = ""
   
    if "twitter" in update.message.text:
        link = update.message.text

    if "tiktok" in update.message.text:
        link = update.message.text

    if link == "":
        print("Couldn't find anything to download.")
        return

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
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("***REMOVED***", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("errors", errors_command))
    dp.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - parse the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, parse))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
