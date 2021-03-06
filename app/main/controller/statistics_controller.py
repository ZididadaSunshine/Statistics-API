import datetime
from datetime import timedelta

from flask import request
from flask_restplus import Resource

from app.main.dto.statistics_dto import StatisticsDTO
from app.main.service.statistics_service import get_overview, get_average, get_trending_keywords

api = StatisticsDTO.api

ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
GRANULARITIES = {
    'hour': timedelta(hours=1),
    'halfday': timedelta(hours=12),
    'day': timedelta(days=1),
    'week': timedelta(weeks=1)
}


def _parse_date(date):
    """ Parse a date and remove any minutes, seconds and microseconds."""
    return datetime.datetime.strptime(date, ISO_FORMAT).replace(minute=0, second=0, microsecond=0)


def _get_granularity_span(granularity):
    return GRANULARITIES.get(granularity, None)


@api.route('/<string:granularity>/brand')
class BrandStatisticsResource(Resource):
    @api.doc('Retrieve an average of the combined sentiment for the requested synonyms.')
    @api.expect(StatisticsDTO.synonyms, validate=True)
    def post(self, granularity):
        synonyms = request.json['synonyms']

        # Check if granularity is supported
        granularity_span = _get_granularity_span(granularity)
        if not granularity_span:
            return dict(message=f'Unsupported granularity {granularity}.'), 400

        return get_average(granularity_span, synonyms)


@api.route('/<string:granularity>/overview')
class OverviewStatisticsResource(Resource):
    @api.doc('Retrieve an overview from a time range and a granularity.')
    @api.expect(StatisticsDTO.timerange, validate=True)
    def post(self, granularity):
        spans_from = _parse_date(request.json['from'])
        spans_to = _parse_date(request.json['to'])
        synonyms = request.json['synonyms']

        # Check if granularity is supported
        granularity_span = _get_granularity_span(granularity)
        if not granularity_span:
            return dict(message=f'Unsupported granularity {granularity}.'), 400

        # Check if there is a mismatch between granularity and time range
        if (spans_to - spans_from) < granularity_span:
            return dict(message=f'Expected granularity to be greater or equal to time range.'), 400

        return get_overview(spans_from, spans_to, granularity_span, synonyms)


@api.route('/<string:granularity>/trending')
class TrendingKeywordsResource(Resource):
    @api.doc('Retrieve trending keywords from a time range and a granularity.')
    @api.expect(StatisticsDTO.synonyms, validate=True)
    def post(self, granularity):
        synonyms = request.json['synonyms']

        # Check if granularity is supported
        granularity_span = _get_granularity_span(granularity)
        if not granularity_span:
            return dict(message=f'Unsupported granularity {granularity}.'), 400

        return get_trending_keywords(granularity_span, synonyms)
