from flask import Blueprint
from flask_restplus import Api

from app.main.controller.snapshot_controller import api as snapshot_namespace

blueprint = Blueprint('sc-statistics', __name__, url_prefix='/api')

api = Api(blueprint, title='SentiCloud Statistics', version='1.0')

# Add namespaces to API
api.add_namespace(snapshot_namespace, path='/snapshots')
