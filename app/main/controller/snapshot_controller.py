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
    ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
    EXPECTED_PROPERTIES = {'posts', 'keywords'}
    MIN_CLASSES_REQUIRED = 2

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

        # Confirm that all required classes are provided
        if len(statistics) < self.MIN_CLASSES_REQUIRED:
            return dict(message='Invalid amount of classes specified.'), 400

        # Confirm that statistics for all classes are provided
        for stat_class in statistics:
            for expected in self.EXPECTED_PROPERTIES:
                if expected not in statistics[stat_class]:
                    return dict(message=f'Expected property {expected} in class {stat_class}.'), 400

        return service.add_snapshot(sentiment, statistics, spans_from, spans_to, synonym)
