import datetime
from datetime import timedelta

from flask_restplus import Resource

from app.main.dto.statistics_dto import StatisticsDTO
from app.main.service.statistics_service import get_from_range

api = StatisticsDTO.api


@api.route('/<string:synonym>/<string:granularity>/<string:from_date>/<string:to_date>')
class StatisticsResource(Resource):
    ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'
    GRANULARITIES = {'hour': timedelta(hours=1),
                     'day': timedelta(days=1),
                     'week': timedelta(weeks=1)}

    @api.doc('Retrieve statistics from a time range.')
    def post(self, synonym, granularity, from_date, to_date):
        spans_from = datetime.datetime.strptime(from_date, self.ISO_FORMAT)
        spans_to = datetime.datetime.strptime(to_date, self.ISO_FORMAT)

        # Check if granularity is supported
        if granularity not in self.GRANULARITIES:
            return dict(message=f'Unsupported granularity {granularity}.'), 400

        # Check if there is a mismatch between granularity and time range
        granularity = self.GRANULARITIES[granularity]
        if (spans_to - spans_from) < granularity:
            return dict(message=f'Expected granularity to be greater or equal to time range.'), 400

        return get_from_range(spans_from, spans_to, granularity, synonym)
