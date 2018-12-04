from app.main.model.snapshot_model import Snapshot
from app.main.model.synonym_model import Synonym


def in_range(snap, min, max):
    return snap.spans_from < max and snap.spans_to >= min


def get_from_range(spans_from, spans_to, granularity, synonym):
    snapshots = Snapshot.query.select_from(Synonym).filter_by(synonym=synonym).join(Synonym.snapshots).\
        filter((Snapshot.spans_from >= spans_from) & (Snapshot.spans_to <= spans_to)).all()

    current_time = spans_from
    statistics = dict()
    while current_time < spans_to:
        current_max_time = current_time + granularity

        contained = [snap for snap in snapshots if in_range(snap, current_time, current_max_time)]
        
        # TODO: Aggregate stats in contained
        current_time = current_max_time

    return statistics

