class Beacon:
    def __init__(self, mac_addr: str, building_id: int, detail_location: str, popular_user_gmail_id: str):
        self.__mac_addr = mac_addr
        self.__building_id = building_id
        self.__detail_location = detail_location  # ex) 208관 1층 강의실 앞 (Exact location where the beacon is installed)
        self.__popular_user_gmail_id = popular_user_gmail_id  # Best user who took the most recommended picture.

    @property
    def mac_addr(self):
        return self.__mac_addr

    @property
    def building_id(self):
        return self.__building_id

    @property
    def detail_location(self):
        return self.__detail_location

    @property
    def popular_user_gmail_id(self):
        return self.__popular_user_gmail_id
