# Overview
Slack bot that responds to interaction with inspring photographs sourced from Unsplash API.

# Usage
Create `config.py` file with Slack and Unsplash app constants.  
Create `users.db` file to store the SQLite user table.  
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
  'scope': 'bot+chat%3Awrite%3Abot'
}
```
Install in virtualenv with modules from requirements.txt.
`python3 app.py` to run OAuth routes and bot.  
