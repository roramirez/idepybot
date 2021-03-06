from .basebot import BaseBot
import requests
import time
import json
import re

class Bot(BaseBot):

    def __init__(self, token):
        super().__init__(token)
        self.last_time_someone_said_keyword = 0
        self.time_interval_between_keyword_detection = 60

    def check_if_user_joined(self, response):
        # If the messsage has the 'new chat participant' key (when a user enters a group)
        if 'new_chat_participant' in response['message']:
            # Check if the new participant has a first name
            if 'first_name' in response['message']['new_chat_participant']:
                # Use the genderize API to know if the name is a male one or a female one
                gender_response = requests.get('https://api.genderize.io/?name={0}'.format(response['message']['new_chat_participant']['first_name']))
                # Change the welcome_message in concordance
                if gender_response.json()['gender'] == 'female':
                    welcome_message = '<b>¡Bienvenida '
                else:
                    welcome_message = '<b>¡Bienvenido '

                welcome_message += '{0}!</b>'.format(response['message']['new_chat_participant']['first_name'])
                json_response = self.send_message(response['message']['chat']['id'], parse_mode='HTML', text=welcome_message)

    def check_if_someone_said_keyword(self, response):
        # If the needed time has passed since the last keyword was detected
        if time.time() > self.last_time_someone_said_keyword + self.time_interval_between_keyword_detection:
            keywords = {
                'ide':'Boh. Todo el mundo sabe que el mejor IDE es <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">Eclipse</a>.',
            }
            # Check if any keyword is being used in the message
            for word in re.sub('[!@#$?]', '', response['message']['text'].lower()).split():
                if word in keywords:
                    json_response = self.send_message(response['message']['chat']['id'], parse_mode='HTML', text=keywords[word], disable_web_page_preview=True)
                    self.last_time_someone_said_keyword = time.time()
                    return True
        return False

    def process_hook(self, response):
        if 'message' in response:
            self.check_if_user_joined(response)

            if 'text' in response['message']:
                self.check_if_someone_said_keyword(response)
