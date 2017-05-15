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

    # Insert or update user authentication information.
    # If a new user (team_id not currently in users table)
    # a bot is started in a thread

    # TODO - clean up thread if updating token

    users = select_all_users()
    if users['status'] == 1:
        for u in users['result']:
            id = u[0]
            team_id = u[4]
            if team_id == auth_response['team_id']:
                update = update_user(id, auth_response['access_token'], auth_response['scope'], auth_response['team_name'], auth_response['team_id'], auth_response['bot']['bot_user_id'], auth_response['bot']['bot_access_token'])
                if update['status'] == 1:
                    return "Authentication updated. Your bot is already running."
                else:
                    return "Could not update authentication. Please try again."
    else:
        return "Could not authenticate. Please try again."

    insert = insert_user(auth_response['access_token'], auth_response['scope'], auth_response['team_name'], auth_response['team_id'], auth_response['bot']['bot_user_id'], auth_response['bot']['bot_access_token'])
    if insert['status'] == 1:
        t = threading.Thread(name=auth_response['team_id'], target=start_bot, args=(auth_response['bot']['bot_user_id'], auth_response['bot']['bot_access_token']))
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
                INSERT INTO users (access_token, scope, team_name, team_id, bot_user_id, bot_access_token) VALUES (?, ?, ?, ?, ?, ?);
                """, (access_token, scope, team_name, team_id, bot_user_id, bot_access_token,))
            result = {'status': 1, 'result': cursor.fetchone }
    except:
        result = {'status': 0, 'result': 'error'}
    return result

def update_user(id, access_token, scope, team_name, team_id, bot_user_id, bot_access_token):
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE users SET access_token = ?, scope = ?, team_name = ?, team_id = ?, bot_user_id = ?, bot_access_token = ? WHERE id = ?;
                """, (access_token, scope, team_name, team_id, bot_user_id, bot_access_token, id,))
            result = {'status': 1, 'result': cursor.fetchone }
    except:
        result = {'status': 0, 'result': 'error'}
    return result

def select_all_users():
    try:
        with sqlite3.connect('users.db') as connection:
           cursor = connection.cursor()
           cursor.execute("""
               SELECT * FROM users ORDER BY id desc;
               """)
           result = {'status': 1, 'result': cursor.fetchall()}
    except:
        result = {'status': 0, 'result': 'error' }
    return result

if __name__ == '__main__':
    users = select_all_users()
    if users['status'] == 1:
        for u in users['result']:
            t = threading.Thread(name=u[4], target=start_bot, args=(u[5], u[6]))
            t.start()
    app.run(debug=True)
