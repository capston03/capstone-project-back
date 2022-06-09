from typing import Dict, Any

from flask import request
from flask_restx import Namespace, Resource

from utility.utilities import to_json
from handler.beacon_DB_handler import beacon_DB_handler

namespace_beacon = Namespace('beacon', 'Api for beacon')


@namespace_beacon.route('/nearby')
class Nearby(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, Any] = request.get_json()
        list_beacon = [params[str(index)] for index in range(len(params))]
        list_beacon = [beacon.get("mac_addr")
                       for beacon in list_beacon]
        try:
            building_id = beacon_DB_handler.get_building_id(list_beacon)
            list_beacon_in_building = beacon_DB_handler.get_all_beacon_in_building(building_id)
            return to_json({index: {
                "mac_addr": beacon.mac_addr,
                "building_id": beacon.building_id,
                "detail_location": beacon.detail_location,
                "popular_user_gmail_id": beacon.popular_user_gmail_id
            } for index, beacon in enumerate(list_beacon_in_building)})
        except Exception as e:
            print(str(e))
            return to_json("error")
