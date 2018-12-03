from enum import IntEnum

from app.main import db
from app.main.model.snapshot_model import Snapshot
from app.main.model.synonym_model import Synonym


class SnapshotServiceResponse(IntEnum):
    Success = 200
    Created = 201
    AlreadyExists = 409


def get_snapshots():
    return Snapshot.query.all()


def add_snapshot(sentiment, statistics, spans_from, spans_to, synonym_str):
    # Add the synonym associated with the snapshot if it does not exist
    synonym = Synonym.query.filter(Synonym.synonym.ilike(synonym_str)).first()
    if not synonym:
        synonym = Synonym(synonym=synonym_str)

        db.session.add(synonym)
        db.session.flush()
        db.session.refresh(synonym)

    # Check for duplicate snapshots
    existing = Snapshot.query.filter((Snapshot.synonym_id == synonym.id) & (Snapshot.spans_from == spans_from)
                                     & (Snapshot.spans_to == spans_to)).first()
    if existing:
        return dict(success=False, message='Snapshot already exists.'), SnapshotServiceResponse.AlreadyExists

    # Create new snapshot
    snapshot = Snapshot(synonym_id=synonym.id, statistics=statistics, sentiment=sentiment, spans_from=spans_from,
                        spans_to=spans_to)

    db.session.add(snapshot)
    db.session.commit()

    return dict(success=True), SnapshotServiceResponse.Created
