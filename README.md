# Overview

Slack bot that responds to interaction with inspring photographs sourced from Unsplash API.

# Usage
Create `config.py` file with Slack and Unsplash app constants.
```
# Unsplash constants
UNSPLASH = {
  'application_id': '<insert-application-id>',
  'application_secret': '<insert-application-secret>',
  'callback_url': 'urn:ietf:wg:oauth:2.0:oob'
}

# Slack bot constants
SLACK = {
  'client_name': 'inspire-me',
  'client_id': '<insert-client-id>',
  'client_secret': '<insert-client-secret>',
  'scope': 'bot'
}
AT_BOT = "<@" + BOT['bot_id'] + ">:"
```
Install in virtualenv modules from requirements.txt.
`SLACK_USER_TOKEN="" SLACK_BOT_TOKEN="" python app.py`
