from handler_db import HandlerDb
from typing import Tuple, List, Final

from model.building import Building
from model.gps_coordinate import GPSCoordinate
from utilities_map import UtilitiesMap


class HandlerMapDb:
    def __init__(self, handler_db: HandlerDb):
        self.__handler_db = handler_db

    def __connect_db(self):
        return self.__handler_db.connect_db()

    RANGE_RADIUS: Final[int] = 5

    # 사용자의 지도 화면 안에 있는 건물들의 리스트를 반환
    def get_list_nearby_building(self,
                                 user_location: GPSCoordinate) -> List[Building]:
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
