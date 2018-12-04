import datetime
from datetime import timedelta

from flask import request
from flask_restplus import Resource

from app.main.dto.statistics_dto import StatisticsDTO

api = StatisticsDTO.api


@api.route('/<string:synonym>/<string:granularity>')
class StatisticsResource(Resource):
    ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'
    GRANULARITIES = {'hour': timedelta(hours=1),
                     'day': timedelta(days=1),
                     'week': timedelta(weeks=1)}

    @api.doc('Retrieve statistics from a time range.')
    @api.expect(StatisticsDTO.timerange, validate=True)
    def post(self, synonym, granularity):
        spans_from = datetime.datetime.strptime(request.json['from'], self.ISO_FORMAT)
        spans_to = datetime.datetime.strptime(request.json['to'], self.ISO_FORMAT)

        # Check if granularity is supported
        if granularity not in self.GRANULARITIES:
            return dict(message=f'Unsupported granularity {granularity}.'), 400

        # Check if there is a mismatch between granularity and time range
        minimum_span = self.GRANULARITIES[granularity]
        if (spans_to - spans_from) < minimum_span:
            return dict(message=f'Expected granularity to be greater or equal to time range.'), 400

        return 'ok'
