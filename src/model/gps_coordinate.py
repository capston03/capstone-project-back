class GPSCoordinate:
    def __init__(self, latitude: float, longitude: float):
        self.__latitude = latitude
        self.__longitude = longitude

    @property
    def coordinate(self):
        return self.__latitude, self.__longitude
