from typing import List, Final

from model.building import Building
from model.gps_coordinate import GPSCoordinate
from utility.utilities_map import UtilitiesMap
from .handler_db import handler_db, HandlerDB


class MapDBHandler:
    def __init__(self, handler_db: HandlerDB):
        self.handler_db = handler_db

    def __connect_db(self):
        """
        Connect to the database (AWS RDS)
        :return: Connection
        """
        return self.handler_db.connect_db()

    # Radius of range (Client gets all buildings that beacon is installed within a five-kilometer radius)
    RANGE_RADIUS: Final[int] = 5

    def get_list_nearby_building(self,
                                 user_location: GPSCoordinate) -> List[Building]:
        """
        Find all bulidings nearby.
        :param user_location: User's location
        :return: List of building
        """
        latitude_range = UtilitiesMap.get_latitude_range(user_location, self.RANGE_RADIUS)
        longitude_range = UtilitiesMap.get_longitude_range(user_location, self.RANGE_RADIUS)
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    print(f"latitude range : {latitude_range[0]} ~ {latitude_range[1]}")
                    print(f"longitude range : {longitude_range[0]} ~ {longitude_range[1]}")
                    sql = f"SELECT * FROM building " \
                          f"WHERE (latitude BETWEEN {latitude_range[0]} AND {latitude_range[1]}) " \
                          f"AND (longitude BETWEEN {longitude_range[0]} AND {longitude_range[1]});"
                    print(sql)
                    cursor.execute(sql)
                    list_building = [Building(int(building[0]),
                                              building[1],
                                              GPSCoordinate(float(building[2]), float(building[3])))
                                     for building in cursor.fetchall()]
                    return list_building
            except Exception as e:
                raise


handler = MapDBHandler(handler_db)
