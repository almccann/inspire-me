import urllib.request
import json
import time
import random
#import logging

import config

#logger = logging.getLogger(__name__)

class Bot(object):

  def __init__(self, slack_client, bot_user_id):
    self.slack_client = slack_client
    self.bot_user_id = bot_user_id

    # HTTP Requests
    self.base = 'https://api.unsplash.com/'
    self.headers = {'Authorization': "Client-ID " + config.UNSPLASH['application_id']}

  def handle_command(self, command, channel):
    if command == 'help':
      text = "@ me with the keyword 'front page' for the latest photos or a 'category' for that category."
      self.slack_client.api_call("chat.postMessage", channel=channel, text=text, as_user=True)
    else:
      self.handle_unsplash_command(command, channel)

  def handle_unsplash_command(self, command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    data = self.request_unsplash(command)
    list = data['content']
    command = data['command']
    content = random.choice(list)
    photographer = content['user']['name']

    if command == 'front page':
      text = 'Some inspiration from the front page by ' + photographer
    elif command == 'not found':
      text = 'Cannot find that category.  But sending you some popular inspiration by ' + photographer
    elif command == 'none':
      text = 'Sending you some popular inspiration by ' + photographer
    else:
      text = 'Sending you some ' + command + ' inspiration by ' + photographer

    attachments = [
      {
        "fallback": "Photo by " + photographer,
        "text": "Photo by " + photographer,
        "image_url": content['urls']['regular'],
        "thumb_url": content['urls']['thumb'],
      }
    ]
    self.slack_client.api_call("chat.postMessage", channel=channel, text=text, attachments=json.dumps(attachments), as_user=True)


  def parse_slack_output(self, slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    at_bot = "<@" + self.bot_user_id + ">"
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and at_bot in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(at_bot)[1].strip().lower(), \
                       output['channel']
    return None, None

  def request_unsplash(self, command = None):
    """
        Request the Unsplash API for images, based on type of request
    """
    if command != None:
      if command.lower() == 'front page'.lower():
        #logger.info('front page command')
        return dict(command='front page', content=self.unsplash_api_get('/photos/curated'))
      elif command == '':
        #logger.info('empty command')
        return dict(command='none', content=self.unsplash_api_get('/photos?order_by=popular'))
      else:
        categories = self.unsplash_api_get('categories')
        for cat in categories:
          if cat['title'].lower() == command.lower():
            #logger.info('category ' + cat['title'].lower() + ' found')
            return dict(command=cat['title'].lower(), content=self.unsplash_api_get('categories/' + str(cat['id']) + '/photos'))
        #logger.info('category not found')
        return dict(command='not found', content=self.unsplash_api_get('/photos?order_by=popular'))

  def unsplash_api_get(self, endpoint):
    """
        Request the Unsplash API at the provided endpoint
    """
    req = urllib.request.Request(self.base + endpoint, headers = self.headers)
    with urllib.request.urlopen(req) as response:
      string = response.read().decode('utf-8')
      return json.loads(string)
