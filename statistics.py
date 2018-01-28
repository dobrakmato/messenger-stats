import datetime
from typing import List, Tuple


def general_stats(self_name: str, conversations: List[Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]]):
    message_count = 0
    conversation_count = 0
    unique_people = set()

    characters_count = 0

    my_messages = 0
    my_characters = 0

    for name, participants, messages in conversations:
        message_count += len(messages)

        for sender, cnts, date in messages:
            characters_count += 0 if cnts is None else len(cnts)

            if sender == self_name:
                my_messages += 1
                my_characters += 0 if cnts is None else len(cnts)

        conversation_count += 1
        unique_people = unique_people | set(participants)

    print(f'You have exchanged {message_count} messages total.')
    print(f'You have sent {my_messages} ({round(my_messages*100/message_count, 2)}%) ' +
          f'messages and received {message_count - my_messages} ' +
          f'({round((message_count - my_messages)*100/message_count, 2)}%) total.')

    print(f'You have exchanged {characters_count} characters in messages total. ' +
          f'({round(my_characters*100/characters_count, 2)}% were sent by you)')

    print(f'You are in {conversation_count} conversations.')
    print(f'You talked to {len(unique_people)} different people.')


def hourly_histogram(conversations: List[Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]]):
    histo = [0 for _ in range(24)]

    for name, participants, messages in conversations:
        for sender, cnts, date in messages:
            histo[date.hour] += 1

    print('Hourly histogram (You exchange most messages at):')
    for i in range(24):
        print(f'{i:02}:00 - {i+1:02}:00\t{histo[i]}')


def years_histogram(conversations: List[Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]]):
    histo = [0 for _ in range(100)]

    for name, participants, messages in conversations:
        for sender, cnts, date in messages:
            histo[date.year - 2000] += 1

    print('Yearly histogram (You exchange most messages in the year):')
    for i in range(100):
        if histo[i] != 0:
            print(f'{i+2000}\t{histo[i]}')


def day_in_week_histogram(conversations: List[Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]]):
    histo = [0 for _ in range(7)]

    for name, participants, messages in conversations:
        for sender, cnts, date in messages:
            histo[int(date.strftime('%w'))] += 1

    print('Day in week histogram (You exchange most messages at):')
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    for i in range(6):
        print(f'{days[i]}\t{histo[i]}')


def msg_lenghts(self_name: str, conversations: List[Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]]):
    self_max = 0
    self_total = 0
    self_cnt = 0

    other_max = 0
    other_total = 0
    other_cnt = 0

    for name, participants, messages in conversations:
        for sender, cnts, date in messages:
            if cnts is not None:
                l = len(cnts)

                if sender == self_name:
                    self_total += l
                    self_max = max(self_max, l)
                    self_cnt += 1
                else:
                    other_total += l
                    other_max = max(other_max, l)
                    other_cnt += 1

    print(f'Longest message has {max(self_max, other_max)} characters')
    print(f'  Your longest message has {self_max} characters')
    print(f'  Longest message you received has {other_max} characters')

    print(f'Average message length is {round((self_total+other_total)/(self_cnt+other_cnt), 2)} characters')
    print(f'  Your average is {round(self_total/self_cnt, 2)} characters')
    print(f'  Average of messages you received {round(other_total/other_cnt, 2)} characters')

    print(f'Based on {self_cnt+other_cnt} messages')


def top_conversations_by_chars(self_name: str,
                               conversations: List[Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]],
                               exhaustive_lists: bool):
    convos = {}
    total_msgs = 0

    for name, participants, messages in conversations:
        total_msgs += len(messages)

        if not str(participants) in convos:
            convos[name] = [0, 0]  # others, me

        for sender, cnts, date in messages:
            if sender == self_name:
                convos[name][1] += 0 if cnts is None else len(cnts)
            else:
                convos[name][0] += 0 if cnts is None else len(cnts)

    top_convos = reversed(sorted((value[0] + value[1], key, value) for (key, value) in convos.items()))

    threshold = total_msgs / len(conversations)

    print('Conversations by characters exchanged:')
    for chars, convo, counts in top_convos:
        if chars != 0:
            if exhaustive_lists or chars > threshold:
                print(f'{convo}\t{chars} ({counts[1]} sent, {counts[0]} received)')

    if not exhaustive_lists:
        print('And more...')


def top_conversations_by_messages(self_name: str,
                                  conversations: List[Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]],
                                  exhaustive_lists: bool):
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

    threshold = total_msgs / len(conversations)

    print('Conversations by messages exchanged:')
    for msgs, convo, counts in reversed(top_convos):
        if msgs != 0:
            if exhaustive_lists or msgs > threshold:
                print(f'{convo}\t{msgs} ({counts[1]} sent, {counts[0]} received)')

    if not exhaustive_lists:
        print('And more...')


def conversation_people_variability(self_name: str,
                                    conversations: List[
                                        Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]]):
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


def msgs_before_reply(self_name: str,
                      conversations: List[Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]]):
    me_msgs = 0
    oth_msgs = 0

    me_responses = 0
    oth_responses = 0

    last = 'me'

    for name, participants, messages in conversations:
        for sender, cnts, date in messages:
            if sender == self_name:
                me_msgs += 1
                if not last == 'me':
                    me_responses += 1
                last = 'me'
            else:
                oth_msgs += 1
                if last == 'me':
                    oth_responses += 1
                last = 'oth'

    print(f'On average other person responded after {round(me_msgs/me_responses, 2)} your messages.')
    print(f'On average you responded after {round(oth_msgs/oth_responses, 2)} messages from other person.')


def time_before_reply(self_name: str,
                      conversations: List[Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]]):
    me_seconds_to_response = 0
    oth_seconds_to_response = 0

    me_responses = 0
    oth_responses = 0

    last = None
    last_my_response = None
    last_oth_response = None

    for name, participants, messages in conversations:
        for sender, cnts, date in messages:
            if sender == self_name:
                last_my_response = date
                if not last == 'me':
                    me_responses += 1
                    me_seconds_to_response += abs((date - last_oth_response).total_seconds())
                last = 'me'
            else:
                last_oth_response = date
                if last == 'me':
                    oth_responses += 1
                    oth_seconds_to_response += abs((date - last_my_response).total_seconds())
                last = 'oth'

    print(f'On average other person responded after {round(me_seconds_to_response/me_responses, 2)} seconds.')
    print(f'On average you responded after {round(oth_seconds_to_response/oth_responses, 2)} seconds.')


def most_used_words(self_name: str,
                    conversations: List[Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]],
                    exhaustive_lists: bool):
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


def who_started_conv(self_name: str,
                     conversations: List[Tuple[str, List[str], List[Tuple[str, str, datetime.datetime]]]]):
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
