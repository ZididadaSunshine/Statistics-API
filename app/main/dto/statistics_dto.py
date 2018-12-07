from flask_restplus import fields, Namespace


class StatisticsDTO:
    api = Namespace('Statistics', description='Statistics operations.')

    timerange = api.model('Time range', {
        'from': fields.DateTime(required=True, description='The date and time which the time range spans from.'),
        'to': fields.DateTime(required=True, description='The date and time which the time range spans to.'),
        'synonyms': fields.List(required=True, cls_or_instance=fields.String,
                                description='List of synonyms to make statistics for.'),
        'granularity': fields.String(required=True, description='The granularity of the returned statistics')
    })
