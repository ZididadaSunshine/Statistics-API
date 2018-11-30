from flask_restplus import Resource

from app.main.dto.snapshot_dto import SnapshotDTO
from app.main.service import snapshot_service as service

api = SnapshotDTO.api


@api.route('')
class SnapshotsResource(Resource):
    @api.doc('test')
    # TODO: Expect time range
    def get(self):
        service.get_snapshots()

        return ''

