from datetime import datetime
from typing import List


class Sticker:
    def __init__(self,
                 id: str, orig_img_path: str, sticker_path: str,
                 uploader_gmail_id: str, upload_time: str,
                 beacon_mac: str, foreground_rect: List[int]):
        self.id = id
        self.orig_img_path = orig_img_path
        self.sticker_path = sticker_path
        self.uploader_gmail_id = uploader_gmail_id
        self.upload_time = upload_time
        self.beacon_mac = beacon_mac
        self.foreground_rect = " ".join(["{:d}".format(point) for point in foreground_rect])
