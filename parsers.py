from html.parser import HTMLParser


class HTMLMessagesParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.started = False
        self.state = 'header'  # message, meta, meta_user, meta_date, header

        # parsed data
        self.participants = []
        self.messages = []
        self.current_message = ('name', 'message', 'time')

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and ('class', 'thread') in attrs:
            self.started = True
            return

        if self.started:
            if self.state == 'meta':
                if ('class', 'user') in attrs:
                    self.state = 'meta_user'
                if ('class', 'meta') in attrs:
                    self.state = 'meta_date'

    def handle_data(self, data: str):
        if self.started:
            if self.state == 'header':
                if ':' in data:
                    self.participants = list(map(str.strip, data[data.index(':') + 1:].strip().split(',')))
                    self.state = 'meta'
            elif self.state == 'meta_user':
                self.current_message = (data, None, None)
                self.state = 'meta'
            elif self.state == 'meta_date':
                self.current_message = (self.current_message[0], None, data)
                self.state = 'message'
            elif self.state == 'message':
                msg = (self.current_message[0], data, self.current_message[2])
                self.messages.append(msg)
                self.current_message = (None, None, None)
                self.state = 'meta'

    def handle_endtag(self, tag):
        if self.state == 'message' and tag == 'p':
            msg = (self.current_message[0], None, self.current_message[2])
            self.messages.append(msg)
            self.current_message = (None, None, None)
            self.state = 'meta'

    def error(self, message):
        print("Parsing Error: ", message)


class HTMLMessageIndexParser(HTMLParser):
    def __init__(self, ignore_facebook_user: bool = True):
        super().__init__()
        self.state = 0
        self.ignore_facebook_user = ignore_facebook_user
        self.current_link = ('link', 'name')
        self.links = []

    def handle_starttag(self, tag, attrs):
        if self.state == 0 and tag == 'div' and ('class', 'contents') in attrs:
            self.state = 1
        if self.state == 1 and tag == 'h1':
            self.state = 2
        if self.state == 2 and tag == 'a':
            self.state = 3
            self.current_link = (attrs[0][1][9:], None)

    def handle_data(self, data: str):
        if self.state == 3:
            self.current_link = (self.current_link[0], data)
            if not self.ignore_facebook_user or data != 'Facebook User':
                self.links.append(self.current_link)
            self.current_link = (None, None)
            self.state = 2

    def error(self, message):
        print("Parsing Error: ", message)
