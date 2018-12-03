from flask_restplus import fields, Namespace


class SnapshotDTO:
    api = Namespace('Snapshot', description='Snapshot operations.')

    snapshot = api.model('Snapshot details', {
        'from': fields.DateTime(required=True, description='The date and time which the snapshots spans from.'),
        'to': fields.DateTime(required=True, description='The date and time which the snapshots spans to.'),
        'statistics': fields.String(required=True,
                                    description='A JSON-encoded dictionary of statistics for each sentiment class.'),
        'synonym': fields.String(required=True, description='The synonym associated with this snapshot.'),
        'sentiment': fields.Float(required=True, description='The average sentiment score for this snapshot.'),
        'id': fields.String(description='An optional identifier which can be used by the client to determine which'
                                        'snapshots could not be created.')
    })
