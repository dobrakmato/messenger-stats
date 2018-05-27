from typing import List
from custom_types import NamedConversation
from utils import safe_div


def general_stats(self_name: str, conversations: List[NamedConversation]):
    """
    Generates general statistics for specified list of conversations.
    :param self_name: name of the person which should be considered as "myself"
    :param conversations: list of conversations
    :return: 
    """
    message_count = 0
    conversation_count = 0
    unique_people = set()

    characters_count = 0

    my_messages = 0
    my_characters = 0

    for _, participants, messages in conversations:
        message_count += len(messages)

        for sender, text, _ in messages:
            characters_count += 0 if text is None else len(text)

            if sender == self_name:
                my_messages += 1
                my_characters += 0 if text is None else len(text)

        conversation_count += 1
        unique_people = unique_people | set(participants)

    print(f'You have exchanged {message_count} messages total.')
    print(f'You have sent {my_messages} ({round(safe_div(my_messages*100, message_count), 2)}%) ' +
          f'messages and received {message_count - my_messages} ' +
          f'({round(safe_div((message_count - my_messages)*100, message_count), 2)}%) total.')

    print(f'You have exchanged {characters_count} characters in messages total. ' +
          f'({round(safe_div(my_characters*100, characters_count), 2)}% were sent by you)')

    print(f'You are in {conversation_count} conversations.')
    print(f'You talked to {len(unique_people)} different people.')


def hourly_histogram(conversations: List[NamedConversation]):
    """
    Generates hourly histogram of messages sent from specified list of conversations.
    :param conversations: list of conversations
    :return: 
    """
    hours = [0 for _ in range(24)]

    for name, participants, messages in conversations:
        for sender, text, date in messages:
            hours[date.hour] += 1

    print('Hourly histogram (You exchange most messages at):')
    for i in range(24):
        print(f'{i:02}:00 - {i+1:02}:00\t{hours[i]}')


def yearly_histogram(conversations: List[NamedConversation]):
    """
    Generates yearly histogram of messages sent from specified list of conversations.
    :param conversations: list of conversations
    :return: 
    """

    # Should be enough for next approximately 100 years.
    years = [0 for _ in range(100)]

    for name, participants, messages in conversations:
        for sender, text, date in messages:
            years[date.year - 2000] += 1

    print('Yearly histogram (You exchange most messages in the year):')
    for i in range(100):
        if years[i] != 0:
            print(f'{i+2000}\t{years[i]}')


def day_in_week_histogram(conversations: List[NamedConversation]):
    """
    Generates yearly histogram of messages sent from specified list of conversations.
    :param conversations: list of conversations
    :return: 
    """
    day_in_week = [0 for _ in range(7)]

    # Names are indexed the same way the days are indexed in strftime()
    # method as specified by Python documentation "Weekday as a decimal number [0(Sunday),6]."
    day_in_week_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    for name, participants, messages in conversations:
        for sender, text, date in messages:
            day_in_week[int(date.strftime('%w'))] += 1

    print('Day in week histogram (You exchange most messages at):')
    for i in range(7):
        print(f'{day_in_week_names[i]}\t{day_in_week[i]}')


def messages_lengths(self_name: str, conversations: List[NamedConversation]):
    """
    Generates statistics about message length from specified list of conversations.
    :param self_name: name of the person which should be considered as "myself"
    :param conversations: list of conversations
    :return: 
    """
    self_max = 0
    self_total = 0
    self_cnt = 0

    other_max = 0
    other_total = 0
    other_cnt = 0

    for name, participants, messages in conversations:
        for sender, text, date in messages:
            # Some messages (eg. when sending image only) have no text content so
            # we need to check that before actually computing length of the text.
            if text is not None:
                message_length = len(text)

                if sender == self_name:
                    self_total += message_length
                    self_max = max(self_max, message_length)
                    self_cnt += 1
                else:
                    other_total += message_length
                    other_max = max(other_max, message_length)
                    other_cnt += 1

    print(f'Longest message has {max(self_max, other_max)} characters')
    print(f'  Your longest message has {self_max} characters')
    print(f'  Longest message you received has {other_max} characters')

    print(f'Average message length is {round(safe_div((self_total+other_total), (self_cnt+other_cnt)), 2)} characters')
    print(f'  Your average is {round(safe_div(self_total, self_cnt), 2)} characters')
    print(f'  Average of messages you received {round(safe_div(other_total, other_cnt), 2)} characters')

    print(f'Based on {self_cnt+other_cnt} messages')


def top_conversations_by_chars(self_name: str, conversations: List[NamedConversation], exhaustive_lists: bool):
    """
    Generates list of top conversations ordered by characters exchanged from specified
    list of conversations.
    
    :param self_name: name of the person which should be considered as "myself"
    :param conversations: list of conversations
    :param exhaustive_lists: whether the list should include all conversations
    :return: 
    """
    conversation_counts = {}
    total_messages = 0  # Used for computing threshold when not using exhaustive lists.

    for name, participants, messages in conversations:
        total_messages += len(messages)

        # Create counters for each conversation not present in list of conversations.
        if not str(participants) in conversation_counts:
            conversation_counts[name] = [0, 0]  # others, me

        for sender, text, _ in messages:
            if sender == self_name:
                conversation_counts[name][1] += 0 if text is None else len(text)
            else:
                conversation_counts[name][0] += 0 if text is None else len(text)

    top_conversations = reversed(
        sorted((value[0] + value[1], key, value) for (key, value) in conversation_counts.items()))

    # Threshold is used to prevent outputting lot of conversations
    # with very little messages. Currently it is calculated as average
    # message count in conversation.
    threshold = safe_div(total_messages, len(conversation_counts))

    print('Conversations by characters exchanged:')
    for characters, conversation_name, counts in top_conversations:
        if characters != 0:
            if exhaustive_lists or characters > threshold:
                print(f'{conversation_name}\t{characters} ({counts[1]} sent, {counts[0]} received)')

    if not exhaustive_lists:
        print('And more...')


def top_conversations_by_messages(self_name: str, conversations: List[NamedConversation], exhaustive_lists: bool):
    """
    Generates list of top conversations ordered by messages exchanged from specified
    list of conversations.

    :param self_name: name of the person which should be considered as "myself"
    :param conversations: list of conversations
    :param exhaustive_lists: whether the list should include all conversations
    :return: 
    """
    conversation_counts = {}
    total_messages = 0  # Used for computing threshold when not using exhaustive lists.

    for name, participants, messages in conversations:
        total_messages += len(messages)

        # Create counters for each conversation not present in list of conversations.
        if not str(participants) in conversation_counts:
            conversation_counts[name] = [0, 0]  # others, me

        for sender, _, _ in messages:
            if sender == self_name:
                conversation_counts[name][1] += 1
            else:
                conversation_counts[name][0] += 1

    top_conversations = sorted((value[0] + value[1], key, value) for (key, value) in conversation_counts.items())

    # Threshold is used to prevent outputting lot of conversations
    # with very little messages. Currently it is calculated as average
    # message count in conversation.
    threshold = safe_div(total_messages, len(conversations))

    print('Conversations by messages exchanged:')
    for messages, conversation_name, counts in reversed(top_conversations):
        if messages != 0:
            if exhaustive_lists or messages > threshold:
                print(f'{conversation_name}\t{messages}' +
                      f' ({round(safe_div(messages, total_messages) * 100, 2)}% of all msgs)' +
                      f' ({counts[1]} sent, {counts[0]} received)')

    if not exhaustive_lists:
        print('And more...')


def conversation_people_variability(self_name: str, conversations: List[NamedConversation]):
    convos = {}
    total_msgs = 0

    for name, participants, messages in conversations:
        total_msgs += len(messages)

        if not str(participants) in convos:
            convos[name] = [0, 0]  # others, me

        for sender, cnts, date in messages:
            if sender == self_name:
                convos[name][1] += 1
            else:
                convos[name][0] += 1

    top_convos = sorted((value[0] + value[1], key, value) for (key, value) in convos.items())

    for i in range(1, 20):
        messages_seen = 0
        people_seen = 0
        for msgs, convo, counts in reversed(top_convos):
            if msgs != 0:
                messages_seen += msgs
                people_seen += 1

                if messages_seen > int(total_msgs / (1 + 0.1 * i)):
                    print(f'{100//(1 + 0.1 * i)}% messages were sent by {people_seen} people.')
                    break


def msgs_before_reply(self_name: str, conversations: List[NamedConversation]):
    me_msgs = 0
    oth_msgs = 0

    me_responses = 0
    oth_responses = 0

    last = 'me'

    for name, participants, messages in conversations:
        for sender, cnts, date in messages:
            if sender == self_name:
                me_msgs += 1
                if last == 'oth':
                    me_responses += 1
                last = 'me'
            else:
                oth_msgs += 1
                if last == 'me':
                    oth_responses += 1
                last = 'oth'

    print(f'On average other person responded after {round(safe_div(me_msgs, me_responses), 2)} your messages.')
    print(f'On average you responded after {round(safe_div(oth_msgs, oth_responses), 2)} messages from other person.')


def time_before_reply(self_name: str, conversations: List[NamedConversation]):
    me_seconds_to_response = 0
    oth_seconds_to_response = 0

    me_responses = 0
    oth_responses = 0

    for name, participants, messages in conversations:
        last = None
        last_my_response = None
        last_oth_response = None

        for sender, cnts, date in messages:
            if sender == self_name:
                last_my_response = date
                if last == 'oth':
                    me_responses += 1
                    me_seconds_to_response += abs((date - last_oth_response).total_seconds())
                last = 'me'
            else:
                last_oth_response = date
                if last == 'me':
                    oth_responses += 1
                    oth_seconds_to_response += abs((date - last_my_response).total_seconds())
                last = 'oth'

    print(f'On average other person responded ' +
          f'after {round(safe_div(me_seconds_to_response, me_responses), 2)} seconds.')
    print(f'On average you responded after {round(safe_div(oth_seconds_to_response, oth_responses), 2)} seconds.')


def most_used_words(self_name: str, conversations: List[NamedConversation], exhaustive_lists: bool):
    words = {}
    my_words = {}

    for name, participants, messages in conversations:
        for sender, cnts, date in messages:
            if cnts is not None:
                message_words = cnts.replace(',', '').strip().split()

                if sender == self_name:
                    for word in message_words:
                        if word not in my_words:
                            my_words[word] = 0
                        else:
                            my_words[word] += 1
                else:
                    for word in message_words:
                        if word not in words:
                            words[word] = 0
                        else:
                            words[word] += 1

    top_words = sorted((value, key) for (key, value) in words.items())
    my_top_words = sorted((value, key) for (key, value) in my_words.items())

    print(f'There are {len(top_words)} different words in conversation(s).')
    print(f'You used {len(my_top_words)} different words.')
    print()
    print('Most used words in conversations:')
    i = 0
    for count, word in reversed(top_words):
        if i < 100 or exhaustive_lists:
            print(f'{word}\t{count}')
        i += 1

    print()
    print('Most used words by you:')
    i = 0
    for count, word in reversed(my_top_words):
        if i < 100 or exhaustive_lists:
            print(f'{word}\t{count}')
        i += 1


def who_started_conv(self_name: str, conversations: List[NamedConversation]):
    me_starts = 0
    oth_starts = 0

    for name, participants, messages in conversations:
        last_msg_at = None
        for sender, cnts, date in messages:
            if last_msg_at is None:
                last_msg_at = date

            ans_after = abs((date - last_msg_at).total_seconds())

            if ans_after > 60 * 30:
                if sender == self_name:
                    me_starts += 1
                else:
                    oth_starts += 1
            last_msg_at = date

    print(f'Other people started conversation with you {oth_starts} times.')
    print(f'You started conversation {me_starts} times.')
