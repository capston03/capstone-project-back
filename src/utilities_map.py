from src.model.gps_coordinate import GPSCoordinate
from haversine import haversine


class UtilitiesMap:
    # Compute distance (unit = km)
    @staticmethod
    def calculate_distance(location0: GPSCoordinate, location1: GPSCoordinate):
        return haversine(location0.coordinate, location1.coordinate)
