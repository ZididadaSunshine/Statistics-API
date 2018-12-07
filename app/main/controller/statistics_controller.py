import datetime
from datetime import timedelta

from flask import request
from flask_restplus import Resource

from app.main.dto.statistics_dto import StatisticsDTO
from app.main.service.statistics_service import get_from_range

api = StatisticsDTO.api


@api.route('')
class StatisticsResource(Resource):
    ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'
    GRANULARITIES = {'hour': timedelta(hours=1),
                     'day': timedelta(days=1),
                     'week': timedelta(weeks=1)}

    @api.doc('Retrieve statistics from a time range.')
    @api.expect(StatisticsDTO.timerange, validate=True)
    def post(self):
        spans_from = datetime.datetime.strptime(request.json['from'], self.ISO_FORMAT)
        spans_to = datetime.datetime.strptime(request.json['to'], self.ISO_FORMAT)
        synonyms = request.json['synonyms']
        granularity = request.json['granularity']

        # Check if granularity is supported
        if granularity not in self.GRANULARITIES:
            return dict(message=f'Unsupported granularity {granularity}.'), 400

        # Check if there is a mismatch between granularity and time range
        granularity = self.GRANULARITIES[granularity]
        if (spans_to - spans_from) < granularity:
            return dict(message=f'Expected granularity to be greater or equal to time range.'), 400

        return get_from_range(spans_from, spans_to, granularity, synonyms)
