from flask import Blueprint
from flask_restx import Api

from namespaces.namespace_beacon import namespace_beacon
from namespaces.namespace_building import namespace_building
from namespaces.namespace_sticker import namespace_sticker
from namespaces.namespace_account import namespace_account

blueprint_user = Blueprint('user', __name__, url_prefix='/user')
api = Api(blueprint_user)
api.add_namespace(namespace_account, '/account')

blueprint_beacon = Blueprint('beacon', __name__, url_prefix='/beacon')
api = Api(blueprint_beacon)
api.add_namespace(namespace_beacon, '/')

blueprint_building = Blueprint('building', __name__, url_prefix='/building')
api = Api(blueprint_building)
api.add_namespace(namespace_building, '/')

blueprint_image = Blueprint('image', __name__, url_prefix='/image')

__blueprint_sticker = Blueprint('sticker', __name__, url_prefix='/sticker')
blueprint_image.register_blueprint(__blueprint_sticker)
api = Api(__blueprint_sticker)
api.add_namespace(namespace_sticker, '/')
