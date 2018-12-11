import datetime
import operator
from functools import reduce


from app.main.model.snapshot_model import Snapshot
from app.main.model.synonym_model import Synonym


def format_chart_date(date):
    return datetime.datetime.strftime(date, '%Y-%m-%d %H:%M:%S')


def average(lst):
    if not lst:
        return 0

    return sum(lst) / float(len(lst))


def sum_posts(lst, cls):
    return sum([item.statistics[cls]['posts'] for item in lst])


def has_synonym(snap, synonym):
    return snap.synonym.synonym == synonym


def in_range(snap, lower, upper):
    # Get how much the date ranges overlap in seconds
    latest_start = max(lower, snap.spans_from)
    earliest_end = min(upper, snap.spans_to)
    overlap = max(0, (earliest_end - latest_start).total_seconds())
    if not overlap:
        return False

    # Get the span of a snap in seconds
    snap_span = (snap.spans_to - snap.spans_from).seconds

    # Return true if the snap overlaps with more than half of the queried span
    return snap_span / overlap > 0.5


def _replace_date(date):
    return date.replace(minute=0, second=0, microsecond=0)


def _get_snapshots(spans_from, spans_to, synonyms):
    spans_from = _replace_date(spans_from)
    spans_to = _replace_date(spans_to)

    return Snapshot.query.select_from(Synonym).filter(Synonym.synonym.in_(synonyms)).join(Synonym.snapshots).\
        filter((Snapshot.spans_from >= spans_from) & (Snapshot.spans_to <= spans_to)).all()


def get_average(granularity_span, synonyms):
    """ Provides the combined average over all the provided synonyms. """
    now = datetime.datetime.utcnow()
    previous = now - granularity_span

    current_average = None
    previous_average = None

    # Only retrieve snapshots once and then use in_range to determine which are in the correct ranges (less queries)
    snapshots = _get_snapshots(now - granularity_span * 2, now, synonyms)

    if snapshots:
        # Compute averages from the current period and the previous
        current_average = average([snap.sentiment for snap in snapshots if in_range(snap, previous, now)])
        previous_average = average([snap.sentiment for snap in snapshots if in_range(snap, previous - granularity_span,
                                                                                     now)])

    return {
        'average': current_average,
        'trend': current_average - previous_average if previous_average else None
    }


def get_overview(spans_from, spans_to, granularity, synonyms):
    """ Provides an overview for all synonyms and for each granularity that fits into it. """
    snapshots = _get_snapshots(spans_from, spans_to, synonyms)

    statistics = {synonym: dict() for synonym in synonyms}
    for synonym in synonyms:
        current_time = spans_from

        while current_time < spans_to:
            current_max_time = current_time + granularity

            # Determine which snapshots are contained in the current time range
            contained = [snap for snap in snapshots if has_synonym(snap, synonym) and in_range(snap,
                                                                                               current_time,
                                                                                               current_max_time)]

            # Skip current timespan if there are no snapshots
            if not contained:
                current_time = current_max_time

                continue

            # Get which classes the snapshots agree on
            all_keys = [snap.statistics.keys() for snap in contained]
            classes = reduce(lambda x, y: x & y, all_keys)

            sentimented_keywords = dict()
            class_statistics = dict()
            # Group keywords by their sentiment. Aggregate their frequency.
            for cls in classes:
                sentimented_keywords[cls] = dict()
                class_statistics[cls] = {'posts': sum_posts(contained, cls)}

                for snapshot in contained:
                    for keyword in snapshot.statistics[cls]['keywords']:
                        if keyword in sentimented_keywords[cls]:
                            sentimented_keywords[cls][keyword] += 1
                        else:
                            sentimented_keywords[cls][keyword] = 1

            # Sort key/value pairs of each sentiment class
            for cls in classes:
                sorted_keywords = sorted(sentimented_keywords[cls].items(), key=operator.itemgetter(1), reverse=True)

                # Take the top 5 keywords according to their frequency
                class_statistics[cls]['keywords'] = [keyword for keyword, frequency in sorted_keywords[:5]]

            statistics[synonym][format_chart_date(current_time)] = {
                'sentiment': average([snap.sentiment for snap in contained]),
                'statistics': class_statistics
            }

            current_time = current_max_time

    return statistics
