import os
import config
import time
import logging
import threading

from flask import Flask, request
from slackclient import SlackClient
from bot import Bot

client_id = config.SLACK['client_id']
client_secret = config.SLACK['client_secret']
oauth_scope = config.SLACK['scope']

# Logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/begin_auth", methods=["GET"])
def pre_install():
  return '''
    <a href="https://slack.com/oauth/authorize?scope={0}&client_id={1}">
      Add to Slack
    </a>
    '''.format(oauth_scope, client_id)

@app.route("/finish_auth", methods=["GET", "POST"])
def post_install():
  # Retrieve the auth code from the request params
  auth_code = request.args['code']

  # An empty string is a valid token for this request
  sc = SlackClient("")

  # Request the auth tokens from Slack
  auth_response = sc.api_call(
    "oauth.access",
    client_id=client_id,
    client_secret=client_secret,
    code=auth_code
  )

  # Save the bot token to an environmental variable or to your data store
  # for later use
  os.environ["SLACK_USER_TOKEN"] = auth_response['access_token']
  os.environ["SLACK_BOT_USER_ID"] = auth_response['bot']['bot_user_id']
  os.environ["SLACK_BOT_TOKEN"] = auth_response['bot']['bot_access_token']

  # Start the bot in a new thread
  t = threading.Thread(name='bot', target=start_bot)
  t.start()

  # Don't forget to let the user know that auth has succeeded!
  return "Auth complete!"

def start_bot():
  slack_client = SlackClient(os.environ["SLACK_BOT_TOKEN"])
  READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
  if slack_client.rtm_connect():
    logger.info("Inspire Me connected with user " + os.environ["SLACK_BOT_USER_ID"])
    while True:
      bot = Bot(slack_client)
      command, channel = bot.parse_slack_output(slack_client.rtm_read())
      if command and channel:
        bot.handle_command(command, channel)
      time.sleep(READ_WEBSOCKET_DELAY)
  else:
    logger.error("Connection failed. Invalid Slack token or bot ID?")
    
if __name__ == '__main__':
  app.run(debug=True)
