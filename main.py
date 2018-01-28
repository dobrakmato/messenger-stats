import sys
import time
import statistics
from parsers import HTMLMessagesParser, HTMLMessageIndexParser, HTMLMyNameParser
from os import path


class FacebookStatistics:
    def __init__(self, root_path: str, encoding: str = 'utf-8'):
        # Settings.
        self.root_path = root_path
        self.encoding = encoding
        self.exclude_group_chats = False
        self.exhaustive_lists = False
        self.ignore_facebook_user = False

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

    def global_stats(self):
        statistics.general_stats(self.my_name, self.conversations)

    def global_hourly_histogram(self):
        statistics.hourly_histogram(self.conversations)

    def global_years_histogram(self):
        statistics.years_histogram(self.conversations)

    def global_day_in_week_histogram(self):
        statistics.day_in_week_histogram(self.conversations)

    def global_msg_lenghts(self):
        statistics.msg_lenghts(self.my_name, self.conversations)

    def top_conversations_by_chars(self):
        statistics.top_conversations_by_chars(self.my_name, self.conversations, self.exhaustive_lists)

    def top_conversations_by_messages(self):
        statistics.top_conversations_by_messages(self.my_name, self.conversations, self.exhaustive_lists)

    def global_conversation_people_variability(self):
        statistics.conversation_people_variability(self.my_name, self.conversations)

    def global_msgs_before_reply(self):
        statistics.msgs_before_reply(self.my_name, self.conversations)

    def global_time_before_reply(self):
        statistics.time_before_reply(self.my_name, self.conversations)

    def global_most_used_words(self):
        statistics.most_used_words(self.my_name, self.conversations, self.exhaustive_lists)

    def globl_who_started_conv(self):
        statistics.who_started_conv(self.my_name, self.conversations)


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

    print('--------------------------------------------------------------')
    stats.global_stats()

    print('--------------------------------------------------------------')
    stats.top_conversations_by_chars()

    print('--------------------------------------------------------------')
    stats.top_conversations_by_messages()

    print('--------------------------------------------------------------')
    stats.global_conversation_people_variability()

    print('--------------------------------------------------------------')
    stats.global_hourly_histogram()

    print('--------------------------------------------------------------')
    stats.global_years_histogram()

    print('--------------------------------------------------------------')
    stats.global_day_in_week_histogram()

    print('--------------------------------------------------------------')
    stats.global_msg_lenghts()

    print('--------------------------------------------------------------')
    stats.global_msgs_before_reply()

    print('--------------------------------------------------------------')
    stats.global_time_before_reply()

    print('--------------------------------------------------------------')
    stats.globl_who_started_conv()

    print('--------------------------------------------------------------')
    stats.global_most_used_words()
