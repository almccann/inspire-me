import time
import logging
from slackclient import SlackClient

import config
from bot import Bot

# Logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

slack_client = SlackClient(config.BOT['bot_token'])

def main():
  READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
  if slack_client.rtm_connect():
    logger.info("Inspire Me connected and running!")
    while True:
      bot = Bot(slack_client)
      command, channel = bot.parse_slack_output(slack_client.rtm_read())
      if command and channel:
        bot.handle_command(command, channel)
      time.sleep(READ_WEBSOCKET_DELAY)
  else:
    logger.error("Connection failed. Invalid Slack token or bot ID?")

if __name__ == "__main__":
  main()