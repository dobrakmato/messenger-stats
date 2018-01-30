import sys
import time
import statistics
import codecs
from parsers import HTMLMessagesParser, HTMLMessageIndexParser, HTMLMyNameParser
from os import path


class FacebookStatistics:
    def __init__(self, root_path: str, encoding: str = 'utf-8'):
        # Settings.
        self.root_path = root_path
        self.encoding = encoding
        self.exclude_group_chats = True
        self.exhaustive_lists = False
        self.ignore_facebook_user = True

        print('Setting: Exclude Group Chats: ', self.exclude_group_chats)
        print('Setting: Ignore Facebook User: ', self.ignore_facebook_user)
        print('Setting: Exhaustive lists: ', self.exhaustive_lists)

        # Data
        self.my_name = None
        self.conversations = []
        self.parse_my_name()

    def parse_my_name(self):
        print('Parsing profile...')
        with open(path.join(self.root_path, 'index.htm'), encoding=self.encoding) as f:
            cnts = f.read()

            parser = HTMLMyNameParser()
            parser.feed(cnts)

            self.my_name = parser.my_name
        print(f'Person name: {self.my_name}')

    def parse_all_messages(self):
        with open(path.join(self.root_path, 'html', 'messages.htm'), encoding=self.encoding) as f:
            cnts = f.read()

            print('Parsing message index...')
            parser = HTMLMessageIndexParser(self.ignore_facebook_user)
            parser.feed(cnts)

            conv_cnt = len(parser.links)

            print(f'Found {conv_cnt} threads.')

            time_start = time.time()
            i = 1
            for link, name in parser.links:
                print(f'\r({i}/{conv_cnt}) Parsing conversation {name}...', end='')
                participants, messages = self.parse_conversation(link)
                if not self.exclude_group_chats or len(participants) == 1:
                    self.conversations.append((name, participants, messages))
                i += 1
            print('')
            print(f'Parsed {i-1} conversations in {time.time() - time_start} seconds')

    def parse_conversation(self, messages_file: str):
        with open(path.join(self.root_path, 'messages', messages_file), encoding=self.encoding) as f:
            cnts = f.read()

            parser = HTMLMessagesParser()
            parser.feed(cnts)

            return parser.participants, parser.messages

    def global_stats(self, conversations):
        statistics.general_stats(self.my_name, conversations)

    def global_hourly_histogram(self, conversations):
        statistics.hourly_histogram(conversations)

    def global_years_histogram(self, conversations):
        statistics.years_histogram(conversations)

    def global_day_in_week_histogram(self, conversations):
        statistics.day_in_week_histogram(conversations)

    def global_msg_lenghts(self, conversations):
        statistics.msg_lenghts(self.my_name, conversations)

    def top_conversations_by_chars(self, conversations):
        statistics.top_conversations_by_chars(self.my_name, conversations, self.exhaustive_lists)

    def top_conversations_by_messages(self, conversations):
        statistics.top_conversations_by_messages(self.my_name, conversations, self.exhaustive_lists)

    def global_conversation_people_variability(self, conversations):
        statistics.conversation_people_variability(self.my_name, conversations)

    def global_msgs_before_reply(self, conversations):
        statistics.msgs_before_reply(self.my_name, conversations)

    def global_time_before_reply(self, conversations):
        statistics.time_before_reply(self.my_name, conversations)

    def global_most_used_words(self, conversations):
        statistics.most_used_words(self.my_name, conversations, self.exhaustive_lists)

    def globl_who_started_conv(self, conversations):
        statistics.who_started_conv(self.my_name, conversations)

    def all_global_stats(self):
        self.all_stats(self.conversations)

    def all_stats(self, conversations):
        print('--------------------------------------------------------------')
        self.global_stats(conversations)

        print('--------------------------------------------------------------')
        self.top_conversations_by_chars(conversations)

        print('--------------------------------------------------------------')
        self.top_conversations_by_messages(conversations)

        print('--------------------------------------------------------------')
        self.global_conversation_people_variability(conversations)

        print('--------------------------------------------------------------')
        self.global_hourly_histogram(conversations)

        print('--------------------------------------------------------------')
        self.global_years_histogram(conversations)

        print('--------------------------------------------------------------')
        self.global_day_in_week_histogram(conversations)

        print('--------------------------------------------------------------')
        self.global_msg_lenghts(conversations)

        print('--------------------------------------------------------------')
        self.global_msgs_before_reply(conversations)

        print('--------------------------------------------------------------')
        self.global_time_before_reply(conversations)

        print('--------------------------------------------------------------')
        self.globl_who_started_conv(conversations)

        print('--------------------------------------------------------------')
        self.global_most_used_words(conversations)


if __name__ == '__main__':
    print('You invoked script as interactive shell.')
    print('--------------------------------------------------------------')
    print('Please enter path to unzipped Facebook export ' +
          'directory (the one which contains subfolders: html, messages).')

    if len(sys.argv) > 1 and len(sys.argv[1]) > 0:
        p = sys.argv[1]
        print('Using provided argument as path: ', sys.argv[1])
    else:
        p = input('Export root: ')

    if not path.isdir(path.join(p, 'html')) or not path.isdir(path.join(p, 'messages')):
        print('--------------------------------------------------------------')
        print('Error: Provided path does not contain required sub-folders html and messages!')
        exit(1)

    print('--------------------------------------------------------------')
    stats = FacebookStatistics(p)
    stats.parse_all_messages()

    stats.all_global_stats()

    print('\n\n')
    print('Printing statistics for each conversation. Conversations with less than 100 messages will be skipped.')
    print('\n\n')

    for conversation in stats.conversations:
        if len(conversation[2]) >= 100:
            print('\n\n')
            print('+============================================================+')
            print(f'|{conversation[0]:^60}|')
            print('|============================================================|')
            stats.all_stats([conversation])
