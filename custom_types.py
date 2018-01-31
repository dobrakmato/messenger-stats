import datetime
from typing import Tuple, List

Message = Tuple[str, str, datetime.datetime]
Participants = List[str]
Conversation = Tuple[Participants, Message]
NamedConversation = Tuple[str, Participants, Message]
