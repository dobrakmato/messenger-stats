import datetime
import json
import os
from json import JSONDecodeError
from os import path
from sys import argv
from time import time
from typing import List

import statistics
from custom_types import NamedConversation
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
        if path.isdir(path.join(self.root_path, 'profile_information')):
            print('Parsing profile...')
            with open(path.join(self.root_path, 'profile_information', 'profile_information.json'),
                      encoding='raw_unicode_escape') as f:

                # Facebook export tool produces invalid JSONs. Here we try to fix
                # wrongly encoded characters.
                encoded = f.read().encode('raw_unicode_escape')
                decoded = encoded.decode()

                # Also some of the control characters are not encoded correctly, so
                # we remove all of them - we are safe to remove line break as JSON is
                # valid without any whitespace.
                for i in range(32):
                    decoded = decoded.replace(chr(i), '')

                try:
                    doc = json.loads(decoded)
                except JSONDecodeError as e:
                    print(">>>>> JSON DECODE ERROR in profile_information")
                    print(e)
                    exit(1)
                    return

            self.my_name = doc['profile']['name']['full_name']
        else:
            separator()
            print('Profile Information section is not included in this export!')
            print('Please provide your name (exactly as on Facebook) so we can ' +
                  'differentiate your messages from messages of your friends.')
            self.my_name = input('Your name (exactly as on Facebook): ').strip()
            separator()
        print(f'Person name: {self.my_name}')

    def parse_all_messages(self) -> None:
        """
        Lists all threads in messages folder and parses each folder as one thread.
        """
        subfolders = os.listdir(path.join(self.root_path, 'messages'))

        time_start = time()
        for subfolder in subfolders:
            i = 0
            folders = os.listdir(path.join(self.root_path,
                                           'messages',
                                           subfolder))

            conversation_count = len(folders)
            print(f'Found {conversation_count} threads in {subfolder}')

            for file in folders:
                # Verify if the message file exists.
                if not os.path.exists(path.join(self.root_path, 'messages', subfolder, file, 'message_1.json')):
                    print(f'Warning: No message.json file for thread {file}! Skipping.')
                    continue

                print(f'({i}/{conversation_count}) Parsing thread {file}...')
                named_conversation = self.parse_conversation(path.join(subfolder, file))
                i += 1

                if named_conversation is None:
                    continue

                # Exclude conversation with self and group conversations if setting is enabled
                if len(named_conversation[1]) > 1:
                    if not (self.exclude_group_chats and len(named_conversation[1]) > 2):
                        self.conversations.append(named_conversation)

        print(f'Parsed {i-1} conversations in {time() - time_start} seconds.')

    def parse_conversation(self, thread_dir: str) -> NamedConversation:
        """
        Parses conversation from JSON file specified by thread_dir parameter and returns
        its participants, title and messages.

        :param thread_dir: directory to parse conversation from (AdamSulko_3c954401d0 for example)
        :return: parsed conversation
        """

        # absolute path to the thread directory
        thread_path = path.join(self.root_path, 'messages', thread_dir)

        # listing all the files in thread directory
        files_in_dir = os.listdir(thread_path)

        parsed_files: List[NamedConversation] = []

        # iterating through the listed files
        for name in files_in_dir:
            # file's absolute path
            name_path = path.join(thread_path, name)

            if ( not os.path.isfile(name_path) ):
                continue

            # parsing the file and appending it to parsed_files if not None
            c = self.parse_file(name_path)
            if ( c != None ):
                parsed_files.append(c)


        # if none of the files have been successfully parsed return None
        if ( len(parsed_files) == 0 ):
            return None

        # appending messages from all parsed files to the first one
        conversation = parsed_files[0]
        for c in parsed_files[1:]:
            conversation[2].extend(c[2])


        return conversation


    def parse_file(self, path: str) -> NamedConversation:
        with open(path, encoding='raw_unicode_escape') as f:

            # Facebook export tool produces invalid JSONs. Here we try to fix
            # wrongly encoded characters.
            encoded = f.read().encode('raw_unicode_escape')
            decoded = encoded.decode()

            # Also some of the control characters are not encoded correctly, so
            # we remove all of them - we are safe to remove line break as JSON is
            # valid without any whitespace.
            for i in range(32):
                decoded = decoded.replace(chr(i), '')

            try:
                doc = json.loads(decoded)
            except JSONDecodeError as e:
                print(">>>>> JSON DECODE ERROR")
                print(e)
                with open('error_file.json', mode='w', encoding='utf-8') as g:
                    g.write(decoded)
                return None

        messages = []
        participants = list(map(lambda x: x['name'], doc.get('participants', set())))

        # Convert JSON message objects to correct structure.
        for msg in reversed(doc['messages']):
            sender_name = msg.get('sender_name', '')

            # Build participants array if the JSON document does not contain this information.
            if isinstance(participants, set):
                participants.add(sender_name)

            if sender_name != '' or not self.ignore_facebook_user:
                messages.append((
                    sender_name,
                    msg.get('content', ''),
                    datetime.datetime.fromtimestamp(msg.get('timestamp_ms') / 1000)
                ))

        return doc.get('title', ' '.join(participants)), list(participants), messages

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
          'directory (the one which contains subfolder messages and JSON files).')

    # Check if user provided argument and wants to use it as root folder for
    # generating statistics from.
    if len(argv) > 1 and len(argv[1]) > 0:
        p = argv[1]
        print('Using provided argument as path: ', argv[1])
    else:
        p = input('Export root: ')

    # Verify that provided path is valid Facebook export archive by checking
    # the presence of most important folders and files.
    if not path.isdir(path.join(p, 'messages')):
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
