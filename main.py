from parsers import HTMLMessagesParser, HTMLMessageIndexParser
from os import path


class FacebookStatistics:
    def __init__(self, root_path: str, encoding: str = 'utf-8'):
        self.root_path = root_path
        self.encoding = encoding
        self.generate_for_all_message()

    def generate_for_all_message(self):
        with open(path.join(self.root_path, 'html', 'messages.htm'), encoding=self.encoding) as f:
            cnts = f.read()

            print('Parsing message index...')
            parser = HTMLMessageIndexParser()
            parser.feed(cnts)
            print(f'Found {len(parser.links)} threads.')

            for link, name in parser.links:
                self.generate_messages(link)

    def generate_messages(self, messages_file: str):
        with open(path.join(self.root_path, 'messages', messages_file), encoding=self.encoding) as f:
            cnts = f.read()

            parser = HTMLMessagesParser()
            parser.feed(cnts)
            print('', parser.participants, 'Messages:', len(parser.messages))
            # print('Messages: ', '\n'.join(list(map(str, parser.messages))))


if __name__ == '__main__':
    # todo: display interactive menu to start.

    stats = FacebookStatistics('C:/Users/Matej/Downloads/facebook-DobrakMato')
    # stats.generate_messages('160.html')
    stats.generate_for_all_message()
