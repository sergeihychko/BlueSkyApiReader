import datetime
from dataclasses import dataclass

@dataclass
class PostData:
    author: str
    uri: str
    txt: str
    queued: bool
    queue_datetime: datetime.datetime

