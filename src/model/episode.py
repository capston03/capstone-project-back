from datetime import datetime
from typing import List, Final


class Episode:
    NOT_DEFINED: Final = -1

    def __init__(self, title: str, content: str,
                 uploader_gmail_id: str, upload_time: str,
                 beacon_mac: str, identifier: int = NOT_DEFINED, heart_rate: int = NOT_DEFINED):
        self.title = title
        self.content = content
        self.uploader_gmail_id = uploader_gmail_id
        self.upload_time = upload_time
        self.beacon_mac = beacon_mac
        self.identifier = identifier
        self.heart_rate = heart_rate
