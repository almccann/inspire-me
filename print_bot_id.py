from slackclient import SlackClient

import config

slack_client = SlackClient(config.SLACK['bot_token'])

if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == config.BOT['bot_name']:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + config.BOT['bot_name'])
