from flask_restplus import fields, Namespace


class StatisticsDTO:
    api = Namespace('Statistics', description='Statistics operations.')

    timerange = api.model('Time range', {
        'from': fields.DateTime(required=True, description='The date and time which the time range spans from.'),
        'to': fields.DateTime(required=True, description='The date and time which the time range spans to.')
    })
