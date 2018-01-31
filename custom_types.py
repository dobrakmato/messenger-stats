import datetime
from typing import NamedTuple, List

Message = NamedTuple('Message', [('sender', str), ('text', str), ('created_at', datetime.datetime)])
Participants = List[str]
Conversation = NamedTuple('Conversation', [('participants', Participants), ('messages', List[Message])])
NamedConversation = NamedTuple('NamedConversation',
                               [('name', str), ('participants', Participants), ('messages', List[Message])])
