from src.model.gps_coordinate import GPSCoordinate


class Building:
    def __init__(self, name: str, location: GPSCoordinate):
        self.__name = name
        self.__location = location

    @property
    def name(self):
        return self.__name

    @property
    def location(self):
        return self.__location
