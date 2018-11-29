from flask_restplus import fields, Namespace


class SnapshotDTO:
    api = Namespace('Snapshot', description='Snapshot operations.')

    snapshot = api.model('Snapshot details', {
        'from': fields.DateTime(required=True, description='The date and time which the snapshots spans from.'),
        'to': fields.DateTime(required=True, description='The date and time which the snapshots spans to.'),
        'keywords': fields.String(required=True,
                                  description='A JSON-encoded dictionary of keywords and their frequency.'),
        'synonym': fields.String(required=True, description='The synonym associated with this snapshot.'),
        'sentiment': fields.Float(required=True, description='The sentiment score for this snapshot.')
    })
