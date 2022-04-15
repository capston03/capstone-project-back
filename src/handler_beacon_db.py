from enum import Enum, auto

from handler_db import HandlerDb
from model.beacon import Beacon
from typing import List


class HandlerBeaconDb:

    def __init__(self, handler_db: HandlerDb):
        self.__handler_db = handler_db

    def __connect_db(self):
        return self.__handler_db.connect_db()

    def get_building_id(self, list_beacon_mac: List[str]):
        list_beacon_mac_str = [f"'{mac_addr}'" for mac_addr in list_beacon_mac]
        str_pool_beacon_mac = f"({', '.join(list_beacon_mac_str)})"
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM beacon " \
                          f"WHERE  mac_addr in {str_pool_beacon_mac};"
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    if len(result) == 0:
                        raise Exception()
                    building_id = int(result[1])
                    return building_id
            except Exception as e:
                raise

    def get_all_beacon_in_building(self, building_id: int) -> List[Beacon]:
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM beacon WHERE building_id = {building_id};"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    if len(result) == 0:
                        raise Exception()
                    list_beacon = [Beacon(beacon[0],
                                          beacon[1],
                                          beacon[2],
                                          beacon[3])
                                   for beacon in result]
                    return list_beacon
            except Exception as e:
                raise
