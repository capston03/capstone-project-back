from typing import Dict

from flask import request
from flask_restx import Namespace, Resource

from model.gps_coordinate import GPSCoordinate
from utility.utilities import to_json, check_if_param_has_keys
from handler.map_DB_handler import map_DB_handler

namespace_building = Namespace('building', 'Api for building')


@namespace_building.route('/nearby')
class Nearby(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["latitude",
                                                "longitude"]):
            return to_json('invalid_input')
        try:
            list_nearby_building = map_DB_handler.get_list_nearby_building(
                GPSCoordinate(
                    float(params.get("latitude")),
                    float(params.get("longitude")))
            )

            return to_json({index: {"id": building.id,
                                    "name": building.name,
                                    "latitude": building.location.coordinate[0],
                                    "longitude": building.location.coordinate[1]
                                    } for index, building in enumerate(list_nearby_building)})
        except Exception as e:
            print(str(e))
            return to_json("error")
