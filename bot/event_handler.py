import json
import logging
import re
import requests

logger = logging.getLogger(__name__)


class RtmEventHandler(object):
    def __init__(self, slack_clients, msg_writer):
        self.clients = slack_clients
        self.msg_writer = msg_writer

    def handle(self, event):

        if 'type' in event:
            self._handle_by_type(event['type'], event)

    def _handle_by_type(self, event_type, event):
        # See https://api.slack.com/rtm for a full list of events
        if event_type == 'error':
            # error
            self.msg_writer.write_error(event['channel'], json.dumps(event))
        elif event_type == 'message':
            # message was sent to channel
            logger.info("There was a message");
            self._handle_message(event)
        elif event_type == 'channel_joined':
            # you joined a channel
            self.msg_writer.write_help_message(event['channel'])
        elif event_type == 'group_joined':
            # you joined a private group
            self.msg_writer.write_help_message(event['channel'])
        else:
            pass

    def _handle_message(self, event):
        # Filter out messages from the bot itself
        if event['user'] and not self.clients.is_message_from_me(event['user']):

            msg_txt = event['text']
            logger.info("MSG text:" + msg_txt)
            
            r = requests.post("http://learn-node-dan121.c9users.io/", data={'message': msg_txt,'user': event['user']})
            logger.info("return: " + str(r.status_code)+" , "+r.reason+" , "+r.text + '...')

            if self.clients.is_bot_mention(msg_txt) and not r.text[0:6] == 'return':
                # e.g. user typed: "@pybot tell me a joke!"
                if 'help' in msg_txt:
                    self.msg_writer.write_help_message(event['channel'])
                elif re.search('hi|hey|hello|howdy', msg_txt):
                    self.msg_writer.write_greeting(event['channel'], event['user'])
                elif 'joke' in msg_txt:
                    self.msg_writer.write_joke(event['channel'])
                elif 'attachment' in msg_txt:
                    self.msg_writer.demo_attachment(event['channel'])
                else:
                    self.msg_writer.write_prompt(event['channel'])
            elif r.text[0:6] == 'return':
                self.msg_writer.send_message(event['channel'], r.text[6:])
