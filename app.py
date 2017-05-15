import config
import time
import logging
import threading
import sqlite3

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

  # TODO - check if user already authenticated, in which case update their existing row rather than inserting a new one.  

  # Store the authentication response for use
  result = insert_user(auth_response['access_token'], auth_response['scope'], auth_response['team_name'], auth_response['team_id'], auth_response['bot']['bot_user_id'], auth_response['bot']['bot_access_token'])

  # Start the bot in a new thread
  if result['status'] == 1:
      t = threading.Thread(name=auth_response['team_name'], target=start_bot, args=(auth_response['bot']['bot_user_id'], auth_response['bot']['bot_access_token']))
      t.start()
      return "Authentication complete. Your bot is now running"
  else:
      return "Could not authenticate. Please try again."

def start_bot(bot_user_id, bot_access_token):
  READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
  
  slack_client = SlackClient(bot_access_token)
  if slack_client.rtm_connect():
    logger.info("Inspire Me connected with user " + bot_user_id)
    while True:
      bot = Bot(slack_client, bot_user_id)
      command, channel = bot.parse_slack_output(slack_client.rtm_read())
      if command and channel:
        bot.handle_command(command, channel)
      time.sleep(READ_WEBSOCKET_DELAY)
  else:
    logger.error("Connection failed. Invalid Slack token or bot ID?")
    
def insert_user(access_token, scope, team_name, team_id, bot_user_id, bot_access_token):
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO users (access_token, scope, team_name, team_id, bot_user_id, bot_access_token) values (?, ?, ?, ?, ?, ?);
                """, (access_token, scope, team_name, team_id, bot_user_id, bot_access_token,))
            result = {'status': 1, 'result': cursor.fetchone }
    except:
        result = {'status': 0, 'result': 'error'}
    return result

def select_all_users():
    try:
        with sqlite3.connect('users.db') as connection:
           cursor = connection.cursor()
           cursor.execute("SELECT * FROM users ORDER BY id desc")
           result = {'status': 1, 'result': cursor.fetchall()}
    except:
        result = {'status': 0, 'result': 'error' }
    return result

if __name__ == '__main__':
    users = select_all_users()
    if users['status'] == 1:
        for u in users['result']:
            t = threading.Thread(name=u[3], target=start_bot, args=(u[5], u[6]))
            t.start()
    app.run(debug=True)
