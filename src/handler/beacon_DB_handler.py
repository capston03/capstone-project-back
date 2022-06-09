from enum import Enum, auto

from model.beacon import Beacon
from typing import List
from DB_handler import DBHandler, DB_handler
from utility.utilities import make_error_message


class BeaconDBHandler:

    def __init__(self, _DB_handler: DBHandler):
        self.__DB_handler = _DB_handler

    def __connect_db(self):
        return self.__DB_handler.connect()

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
                raise Exception(make_error_message(str(e)))

    def get_all_beacon_in_building(self, building_id: int) -> List[Beacon]:
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM beacon WHERE building_id = {building_id};"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    if len(result) == 0:
                        raise Exception()
                    list_beacon = [Beacon(beacon_info[0],
                                          beacon_info[1],
                                          beacon_info[2],
                                          beacon_info[3])
                                   for beacon_info in result]
                    return list_beacon
            except Exception as e:
                raise Exception(make_error_message(str(e)))


beacon_DB_handler = BeaconDBHandler(DB_handler)
