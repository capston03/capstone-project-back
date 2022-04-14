from model.gps_coordinate import GPSCoordinate
from haversine import haversine, inverse_haversine, Direction
from typing import Tuple


class UtilitiesMap:
    # Compute distance (unit = km)
    @staticmethod
    def calculate_distance(location0: GPSCoordinate, location1: GPSCoordinate):
        return haversine(location0.coordinate, location1.coordinate)

    @staticmethod
    def get_latitude_range(location: GPSCoordinate, range_radius: float):
        north_point: Tuple[float, float] = inverse_haversine(location.coordinate, range_radius, Direction.NORTH)
        south_point: Tuple[float, float] = inverse_haversine(location.coordinate, range_radius, Direction.SOUTH)
        return south_point[0], north_point[0]

    @staticmethod
    def get_longitude_range(location: GPSCoordinate, range_radius: float):
        east_point: Tuple[float, float] = inverse_haversine(location.coordinate, range_radius, Direction.EAST)
        west_point: Tuple[float, float] = inverse_haversine(location.coordinate, range_radius, Direction.WEST)
        return west_point[1], east_point[1]
