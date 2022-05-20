from datetime import datetime


class Sticker:
    def __init__(self,
                 id: str, orig_img_path: str, sticker_path: str,
                 uploader_gmail_id: str, upload_time: str,
                 beacon_mac: str):
        self.id = id
        self.orig_img_path = orig_img_path
        self.sticker_path = sticker_path
        self.uploader_gmail_id = uploader_gmail_id
        self.upload_time = upload_time
        self.beacon_mac = beacon_mac
