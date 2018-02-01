import statistics
from time import time
from sys import argv
from typing import List
from custom_types import Conversation, NamedConversation
from parsers import HTMLMessagesParser, HTMLMessageIndexParser, HTMLMyNameParser
from os import path
from utils import separator


class FacebookStatistics:
    """
    Main entry-point.
    """

    def __init__(self, root_path: str, encoding: str = 'utf-8', exclude_group_chats=True, exhaustive_lists=False,
                 ignore_facebook_user=True):
        self.root_path = root_path
        self.encoding = encoding

        # Settings.
        self.exclude_group_chats = exclude_group_chats
        self.exhaustive_lists = exhaustive_lists
        self.ignore_facebook_user = ignore_facebook_user

        self.print_settings()

        # Data
        self.my_name: str = None
        self.conversations: List[NamedConversation] = []
        self.parse_my_name()

    def print_settings(self) -> None:
        """
        Prints current settings to standard output.
        """
        print('Setting: Exclude Group Chats: ', self.exclude_group_chats)
        print('Setting: Ignore Facebook User: ', self.ignore_facebook_user)
        print('Setting: Exhaustive lists: ', self.exhaustive_lists)

    def parse_my_name(self) -> None:
        """
        Parses name of person whose archive is being processed.
        
        Name is than stored as field `my_name`.
        """
        print('Parsing profile...')
        with open(path.join(self.root_path, 'index.htm'), encoding=self.encoding) as f:
            file_content = f.read()

            parser = HTMLMyNameParser()
            parser.feed(file_content)

            self.my_name = parser.my_name
        print(f'Person name: {self.my_name}')

    def parse_all_messages(self) -> None:
        """
        Parses conversations (threads) index and then automatically parses each 
         discovered conversation (thread) by calling the parse_conversation() method.
        """
        with open(path.join(self.root_path, 'html', 'messages.htm'), encoding=self.encoding) as f:
            file_content = f.read()

            print('Parsing message index...')
            parser = HTMLMessageIndexParser(self.ignore_facebook_user)
            parser.feed(file_content)

            conversation_count = len(parser.links)

            print(f'Found {conversation_count} threads.')

            time_start = time()
            i = 1
            for link, name in parser.links:
                print(f'\r({i}/{conversation_count}) Parsing conversation {name}...', end='')
                participants, messages = self.parse_conversation(link)

                # Exclude conversation with self and group conversations if setting is enabled
                if not self.exclude_group_chats or len(participants) == 1:
                    named_conversation = (name, participants, messages)
                    self.conversations.append(named_conversation)
                i += 1
            print('')
            print(f'Parsed {i-1} conversations in {time() - time_start} seconds')

    def parse_conversation(self, messages_file: str) -> Conversation:
        """
        Parses conversation specified by message_file parameter and returns its participants and messages.
        
        :param messages_file: file to parse conversation from (24.html for example) 
        :return: parsed conversation
        """

        with open(path.join(self.root_path, 'messages', messages_file), encoding=self.encoding) as f:
            file_content = f.read()

            parser = HTMLMessagesParser()
            parser.feed(file_content)

            return parser.participants, parser.messages

    def all_stats(self, conversations: List[NamedConversation]):
        """
        Runs all statistics for specified list of conversations.
        :param conversations: list of conversation to run statistics generators on
        :return: 
        """
        for func in [self.global_stats, self.top_conversations_by_chars, self.top_conversations_by_messages,
                     self.conversation_people_variability, self.hourly_histogram, self.years_histogram,
                     self.day_in_week_histogram, self.msg_lenghts, self.msgs_before_reply, self.time_before_reply,
                     self.who_started_conv, self.most_used_words]:
            separator()
            func(conversations)

    def all_global_stats(self):
        self.all_stats(self.conversations)

    # =============================================================
    # Shortcut methods for generating different statistics for this
    # archive and user.
    # =============================================================

    def global_stats(self, conversations: List[NamedConversation]):
        statistics.general_stats(self.my_name, conversations)

    def hourly_histogram(self, conversations: List[NamedConversation]):
        statistics.hourly_histogram(conversations)

    def years_histogram(self, conversations: List[NamedConversation]):
        statistics.yearly_histogram(conversations)

    def day_in_week_histogram(self, conversations: List[NamedConversation]):
        statistics.day_in_week_histogram(conversations)

    def msg_lenghts(self, conversations: List[NamedConversation]):
        statistics.messages_lengths(self.my_name, conversations)

    def top_conversations_by_chars(self, conversations: List[NamedConversation]):
        statistics.top_conversations_by_chars(self.my_name, conversations, self.exhaustive_lists)

    def top_conversations_by_messages(self, conversations: List[NamedConversation]):
        statistics.top_conversations_by_messages(self.my_name, conversations, self.exhaustive_lists)

    def conversation_people_variability(self, conversations: List[NamedConversation]):
        statistics.conversation_people_variability(self.my_name, conversations)

    def msgs_before_reply(self, conversations: List[NamedConversation]):
        statistics.msgs_before_reply(self.my_name, conversations)

    def time_before_reply(self, conversations: List[NamedConversation]):
        statistics.time_before_reply(self.my_name, conversations)

    def most_used_words(self, conversations: List[NamedConversation]):
        statistics.most_used_words(self.my_name, conversations, self.exhaustive_lists)

    def who_started_conv(self, conversations: List[NamedConversation]):
        statistics.who_started_conv(self.my_name, conversations)


if __name__ == '__main__':
    print('You invoked script as interactive shell.')
    separator()
    print('Please enter path to unzipped Facebook export ' +
          'directory (the one which contains subfolders: html, messages).')

    # Check if user provided argument and wants to use it as root folder for
    # generating statistics from.
    if len(argv) > 1 and len(argv[1]) > 0:
        p = argv[1]
        print('Using provided argument as path: ', argv[1])
    else:
        p = input('Export root: ')

    # Verify that provided path is valid Facebook export archive by checking
    # the presence of most important folders and files.
    if not path.isdir(path.join(p, 'html')) or not path.isdir(path.join(p, 'messages')):
        separator()
        print('Error: Provided path does not contain required sub-folders html and messages!')
        exit(1)

    # Everything seems to be alright so let's start parsing everything.
    separator()
    stats = FacebookStatistics(p)
    stats.parse_all_messages()

    # Generate global statistics.
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
