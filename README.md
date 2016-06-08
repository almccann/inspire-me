# Overview

Slack bot that responds to interaction with inspring photographs sourced from Unsplash API.

# Usage
Create `config.py` file with Slack and Unsplash app constants.
```
# Unsplash constants
UNSPLASH = {
  'application_id': 'application-id',
  'application_secret': 'application-secret',
  'callback_url': 'urn:ietf:wg:oauth:2.0:oob'
}

# Slack bot constants
BOT = {
  'bot_name': 'bot-name',
  'bot_token': 'bot-token',
  'bot_id': 'bot-id'
}
AT_BOT = "<@" + BOT['bot_id'] + ">:"
```
Install in virtualenv modules from requirements.txt.
`python start.py`