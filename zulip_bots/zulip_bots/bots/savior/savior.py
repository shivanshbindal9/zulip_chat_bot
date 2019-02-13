import requests
import logging
import re
import urllib
from zulip_bots.lib import Any

from typing import Optional, Any, Dict


# See doc.md for instructions on running this code.

class SaviorHandler(object):
    '''
    This plugin facilitates searching for a
    specific key term, tell jokes, get news and have
    fun with some dl implementations. It looks for messages starting with '@mention-bot'
    '''

    def usage(self) -> str:
        return '''
            This plugin will allow users to directly search
            Wikipedia, get some courses, get jokes, etc. Users
            should preface searches with "@mention-bot".
            @mention-bot help for more'''


    def handle_message(self, message: Dict[str, str], bot_handler: Any) -> None:

        first_word = message['content'].split(' ', 1)[0]
        if first_word == "joke":
            bot_response = self.get_bot_joke_response(message, bot_handler)
        elif first_word == "wikipedia":
            bot_response = self.get_bot_wiki_response(message, bot_handler)
        elif first_word == "teach_me":
            bot_response = self.get_bot_teach_response(message, bot_handler)
        elif first_word == "news":
            bot_response = self.get_bot_news(message, bot_handler)
        elif first_word == "help":
            bot_response = self.get_bot_help_response(message, bot_handler)
        elif first_word == "analyse":
            bot_response = self.get_bot_analyse_response(message, bot_handler)
        elif first_word == "summarize":
            bot_response = self.get_bot_summarise_response(message, bot_handler)
        else:
            bot_response = self.get_bot_reply(message, bot_handler)

        bot_handler.send_reply(message, bot_response)

 
    def get_bot_wiki_response(self, message: Dict[str, str], bot_handler: Any) -> Optional[str]:
        '''This function returns the URLs of the requested topic.'''

        help_text = 'Please enter your search term after {}'

        # Checking if the link exists.
        query = message['content'][10:]
        if query == '':
            return help_text.format(bot_handler.identity().mention)

        query_wiki_url = 'https://en.wikipedia.org/w/api.php'
        query_wiki_params = dict(
            action='query',
            list='search',
            srsearch=query,
            format='json'
        )

        try:
            data = requests.get(query_wiki_url, params=query_wiki_params)
        except requests.exceptions.RequestException:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'

        # Checking if the bot accessed the link.
        if data.status_code != 200:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'

        new_content = 'For search term:' + query + '\n'

        # Checking if there is content for the searched term
        if len(data.json()['query']['search']) == 0:
            new_content = 'I am sorry. The search term you provided is not found :slightly_frowning_face:'
        else:
            for i in range(min(3, len(data.json()['query']['search']))):
                search_string = data.json()['query']['search'][i]['title'].replace(' ', '_')
                url = 'https://en.wikipedia.org/wiki/' + search_string
                new_content += str(i + 1) + ':' + '[' + search_string + ']' + '(' + url.replace('"', "%22") + ')\n'
        return new_content


    def get_bot_joke_response(self, message: Dict[str, str], bot_handler: Any) -> Optional[str]:
        '''This function returns a joke '''

        help_text = 'Please enter your search term after {}'

        # Checking if the link exists.

        query_joke_url = 'https://icanhazdadjoke.com/'

        try:
            data = requests.get(query_joke_url, headers={"Accept": "application/json"})

        except requests.exceptions.RequestException:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'

        # Checking if the bot accessed the link.
        if data.status_code != 200:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'

        # Checking if there is content for the searched term
        if len(data.json()['joke']) == 0:
            new_content = 'I am sorry. The search term you provided is not found :slightly_frowning_face:'
        else:
            new_content = data.json()['joke']
        return new_content


    def get_bot_news(self, message, bot_handler: Any) -> Optional[str]:
        '''This functions returns recent news based on keyword provided by user'''

        help_text = 'Please enter your search term after {}'

        # Checking if the link exists.
        query = message['content'][5:]
        if query == '':
            return help_text.format(bot_handler.identity().mention)

        query_news_url = 'https://newsapi.org/v2/everything?'
        query_news_params = dict(
            apiKey='e7682c2d3cd64221984d798bdc9dff4b',
            language='en',
            pageSize=3,
            q=query
        )
        try:
            data = requests.get(query_news_url, query_news_params)
        except requests.exceptions.RequestException:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now. :slightly_frowning_face:\n' \
                   'Please try again later.'
            # Checking if there is content for the searched term
        if data.status_code != 200:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later. ' + str(data.status_code)

        new_content = 'For search term:' + query + '\n'
        if len(data.json()['articles']) == 0:
            new_content = 'I am sorry. The search term you provided is not found :slightly_frowning_face:'

        else:
            for i in range(min(3, len(data.json()['articles']))):
                author = data.json()['articles'][i]['author']
                title = data.json()['articles'][i]['title']
                description = data.json()['articles'][i]['description']
                url = data.json()['articles'][i]['url']
                if author is None:
                    new_content += str(
                        i + 1) + ': Title: ' + title + '\n   ' + description + '\n (' + url + ') \n'
                else:
                    new_content += str(
                        i + 1) + ': Author: ' + author + '\n   Title: ' + title + '\n   ' + description + '\n (' + url + ') \n'
        return new_content


    def get_bot_teach_response(self, message, bot_handler: Any) -> Optional[str]:
        '''This function returns various courses avialable on different platforms like udemy, coursera, udacity, etc. to help you learn the topic of your choice.'''

        help_text = 'Please enter your search term after {}'

        # Checking if the link exists.
        query = message['content'][8:]
        if query == '':
            return help_text.format(bot_handler.identity().mention)

        query_teach_url = 'https://www.googleapis.com/customsearch/v1'
        query_teach_params = dict(
            key='AIzaSyDWus4C1ykIrL3q7uIYB1MCTIwdM5wfQDo',
            cx='004985854750889686468:okdojnlvqsw',
            q=query,

        )
        try:
            data = requests.get(query_teach_url, params=query_teach_params)

        except requests.exceptions.RequestException:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'

        # Checking if the bot accessed the link.
        if data.status_code != 200:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'

        new_content = 'For search term:' + query + '\n'

        # Checking if there is content for the searched term
        if data.json()['queries']['request'][0]['count'] == 0:
            new_content = 'I am sorry. The search term you provided is not found :slightly_frowning_face:'
        else:
            for i in range(min(3, data.json()['queries']['request'][0]['count'])):
                result_title = data.json()['items'][i]['title']
                url = data.json()['items'][i]['link']
                snippet = data.json()['items'][i]['snippet']

                new_content += 'Title' + ':' + result_title + '\n' + 'Link' + ':' + url + '\n' \
                               + 'Description:' + snippet + '\n' + '\n'
        return new_content


    def get_bot_help_response(self, message, bot_handler: Any) -> Optional[str]:
        ''' This function returns varios functionalities present in the bot'''

        new_content = "A list of functionalities is as given below: \n @Savior wikipedia <Query> \n @Savior teach_me <Topic Name> \n @Savior news <Topic> \n @Savior joke \n @Savior analyse <Url> "\
                      "\n @Savior summarize <text_document_url>"
        return new_content


    def get_bot_reply(self, message, bot_handler: Any) -> Optional[str]:
        '''This function is returned if the query is not correct'''

        new_content = "It is not a valid query \n please check '@Savior help'"
        return new_content


    def get_bot_analyse_response(self, message, bot_handler: Any) -> Optional[str]:
        '''This function helps you analyse any image just by providing its link'''
        help_text = 'Please enter your search term after {}'

        # Checking if the link exists.
        query = message['content'][8:]
        if query == '':
            return help_text.format(bot_handler.identity().mention)

        try:
            data = requests.post(
                "https://api.deepai.org/api/densecap",
                data={
                    'image': query,
                },
                headers={'api-key': 'f408eaa3-9f9a-439a-978c-a3c24eef05c4'}
            )
        except requests.exceptions.RequestException:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'

        # Checking if the bot accessed the link.
        if data.status_code != 200:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'
        new_content = 'Analysing... \n'
        #if len(data.json()['err']) != 0:
            #return 'please enter valid url'
        if len(data.json()['output']['captions']) == 0:
            new_content = 'I am sorry. No object is not found'
        else:
            for i in range(min(5, len(data.json()['output']['captions']))):
                caption = data.json()['output']['captions'][i]['caption']
                confidence = data.json()['output']['captions'][i]['confidence']
                new_content += str(i+1)+' '+caption+' is detected with a confidence of '+str(confidence)+' \n'

        return new_content

    def get_bot_summarise_response(self, message, bot_handler: Any) -> Optional[str]:
        '''This function helps you analyse any image just by providing its link'''
        help_text = 'Please enter your search term after {}'

        # Checking if the link exists.
        query = message['content'][10:]
        if query == '':
            return help_text.format(bot_handler.identity().mention)

        try: 
            data = requests.post(
                "https://api.deepai.org/api/summarization",
                data={
                    'text': query,
                },
                headers={'api-key': 'f408eaa3-9f9a-439a-978c-a3c24eef05c4'}
            )
        except requests.exceptions.RequestException:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'

        # Checking if the bot accessed the link.
        if data.status_code != 200:
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'
        new_content = 'Analysing... \n'
        
        if len(data.json()['output']) == 0:
            new_content = 'I am sorry. No object is not found'
        else:
           new_content = data.json()['output']

        return new_content

        
handler_class = SaviorHandler