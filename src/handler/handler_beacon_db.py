from enum import Enum, auto

from model.beacon import Beacon
from typing import List
from .handler_db import handler_db as db_handler, HandlerDB


class BeaconDBHandler:

    def __init__(self, handler_db: HandlerDB):
        self.__handler_db = handler_db

    def __connect_db(self):
        """
        Connect to the database (AWS RDS).
        :return: Connection
        """
        return self.__handler_db.connect_db()

    def get_building_id(self, list_beacon_mac: List[str]):
        """
        Find id of building that the beacons are installed.
        :param list_beacon_mac: list of beacon mac address.
        :return: building id
        """
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
            except Exception:
                raise

    def get_all_beacon_in_building(self, building_id: int) -> List[Beacon]:
        '''
        Find all beacons installed in this building.
        :param building_id: building id.
        :return: list of beacon.
        '''
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
                raise


handler = BeaconDBHandler(db_handler)
