from gps_coordinate import GPSCoordinate


class Building:
    def __init__(self, id: int, name: str, location: GPSCoordinate):
        self.__id = id
        self.__name = name
        self.__location = location

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def location(self):
        return self.__location
