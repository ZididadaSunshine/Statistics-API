import datetime
import json

from flask import request
from flask_restplus import Resource

from app.main.dto.snapshot_dto import SnapshotDTO
from app.main.service import snapshot_service as service
from app.main.service.snapshot_service import SnapshotServiceResponse

api = SnapshotDTO.api


@api.route('')
class SnapshotsResource(Resource):
    ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'

    @api.doc('Retrieve snapshots from a time range.')
    def get(self):
        encoded = dict()

        for snapshot in service.get_snapshots():
            encoded[snapshot.id] = {'from': snapshot.spans_from.strftime(self.ISO_FORMAT),
                                    'statistics': snapshot.statistics}

        return encoded

    @api.response(SnapshotServiceResponse.AlreadyExists, 'Snapshot already exists.')
    @api.response(SnapshotServiceResponse.Created, 'Snapshot created successfully.')
    @api.doc('Register a snapshot')
    @api.expect(SnapshotDTO.snapshot, validate=True)
    def post(self):
        spans_from = datetime.datetime.strptime(request.json['from'], self.ISO_FORMAT)
        spans_to = datetime.datetime.strptime(request.json['to'], self.ISO_FORMAT)
        synonym = request.json['synonym']
        statistics = json.loads(request.json['statistics'])
        sentiment = request.json['sentiment']

        return service.add_snapshot(sentiment, statistics, spans_from, spans_to, synonym)
