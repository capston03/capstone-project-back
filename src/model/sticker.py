from datetime import datetime
from typing import List


class Sticker:
    def __init__(self,
                 original_img_path: str, thumbnail_path: str, sticker_path: str,
                 foreground_rectangle: List[float],
                 episode_id: int = -1, sticker_id: int = -1):
        self.episode_id = episode_id
        self.original_img_path = original_img_path
        self.thumbnail_path = thumbnail_path
        self.sticker_path = sticker_path
        self.foreground_rectangle = " ".join(["{:.4f}".format(val) for val in foreground_rectangle])
        self.episode_id = episode_id
        self.sticker_id = sticker_id
