from flask import Blueprint
from flask_restplus import Api

from app.main.controller.snapshot_controller import api as snapshot_namespace

blueprint = Blueprint('sw7-statistics-api', __name__, url_prefix='/api')

api = Api(blueprint, title='SW7 Statistics API', version='1.0')

# Add namespaces to API
api.add_namespace(snapshot_namespace, path='/snapshots')
