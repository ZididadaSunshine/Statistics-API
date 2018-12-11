from flask_restplus import fields, Namespace


class StatisticsDTO:
    api = Namespace('Statistics', description='Statistics operations.')

    synonyms = api.model('Synonyms', {
        'synonyms': fields.List(required=True, cls_or_instance=fields.String,
                                description='List of synonyms to make statistics for.'),
    })

    timerange = api.model('Time range', {
        'from': fields.DateTime(required=True, description='The date and time which the time range spans from.'),
        'to': fields.DateTime(required=True, description='The date and time which the time range spans to.'),
        'synonyms': fields.List(required=True, cls_or_instance=fields.String,
                                description='List of synonyms to make statistics for.'),
    })
