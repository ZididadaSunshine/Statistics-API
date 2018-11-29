from flask_restplus import Resource

from app.main.dto.snapshot_dto import SnapshotDTO

api = SnapshotDTO.api


@api.route('')
class SnapshotsResource(Resource):
    @api.doc('test')
    def get(self):
        return ''

