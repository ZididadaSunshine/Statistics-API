import datetime
import operator
import fcntl
import time
from functools import reduce

from app.main.model.snapshot_model import Snapshot
from app.main.model.synonym_model import Synonym

_current_milli_time = lambda: int(round(time.time() * 1000))


def _format_log_date(date):
    return datetime.datetime.strftime(date, '%Y-%m-%d %H:%M:%S.%f')


def _format_chart_date(date):
    return datetime.datetime.strftime(date, '%Y-%m-%d %H:%M:%S')


def _append_line_exclusive(file, contents):
    with open(file, 'a') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        file.write(contents + '\n')
        fcntl.flock(file, fcntl.LOCK_UN)


def _average(lst):
    if not lst:
        return 0

    return sum(lst) / float(len(lst))


def _sum_posts(lst, cls):
    return sum([item.statistics[cls]['posts'] for item in lst])


def _has_synonym(snap, synonym):
    return snap.synonym.synonym == synonym


def _in_range(snap, lower, upper):
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


def _get_snapshots(spans_from, spans_to, synonyms):
    now_ms = _current_milli_time()

    snapshots = Snapshot.query.select_from(Synonym).filter(Synonym.synonym.in_(synonyms)).join(Synonym.snapshots). \
        filter((Snapshot.spans_from >= spans_from) & (Snapshot.spans_to <= spans_to)).all()

    _append_line_exclusive('snapshot_timer.dat',
                           f'{_format_log_date(datetime.datetime.utcnow())}={_current_milli_time() - now_ms}')

    return snapshots


def _get_intersecting_classes(snapshots):
    all_keys = [snap.statistics.keys() for snap in snapshots]
    classes = reduce(lambda x, y: x & y, all_keys)

    return classes


def get_average(granularity_span, synonyms):
    """ Provides the combined average over all the provided synonyms. """
    now = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    previous = now - granularity_span

    current_average = None
    previous_average = None
    posts = 0

    # Only retrieve snapshots once and then use in_range to determine which are in the correct ranges (less queries)
    snapshots = _get_snapshots(now - granularity_span * 2, now, synonyms)
    now_ms = _current_milli_time()

    if snapshots:
        # Compute averages from the current period and the previous
        current_snapshots = [snap for snap in snapshots if _in_range(snap, previous, now)]
        previous_snapshots = [snap for snap in snapshots if _in_range(snap, previous - granularity_span, now)]

        # Get average sentiment values
        current_average = _average([snap.sentiment for snap in current_snapshots])
        previous_average = _average([snap.sentiment for snap in previous_snapshots])

        # Sum posts for all classes in current snapshot period
        if current_snapshots:
            classes = _get_intersecting_classes(current_snapshots)
            posts = reduce(lambda x, y: _sum_posts(current_snapshots, x) + _sum_posts(current_snapshots, y), classes)

    _append_line_exclusive('average_timer.dat',
                           f'{_format_log_date(datetime.datetime.utcnow())}={_current_milli_time() - now_ms}')

    return {
        'sentiment_average': current_average,
        'sentiment_trend': current_average - previous_average if previous_average else None,
        'posts': posts
    }


def get_overview(spans_from, spans_to, granularity, synonyms):
    """ Provides an overview for all synonyms and for each granularity that fits into it. """
    snapshots = _get_snapshots(spans_from, spans_to, synonyms)
    now_ms = _current_milli_time()

    statistics = {synonym: dict() for synonym in synonyms}
    for synonym in synonyms:
        current_time = spans_from

        while current_time < spans_to:
            current_max_time = current_time + granularity

            # Determine which snapshots are contained in the current time range
            contained = [snap for snap in snapshots if _has_synonym(snap, synonym) and _in_range(snap,
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
                class_statistics[cls] = {'posts': _sum_posts(contained, cls)}

                for snapshot in contained:
                    for keyword in snapshot.statistics[cls]['keywords']:
                        if keyword == synonym:
                            continue

                        if keyword in sentimented_keywords[cls]:
                            sentimented_keywords[cls][keyword] += 1
                        else:
                            sentimented_keywords[cls][keyword] = 1

            # Sort key/value pairs of each sentiment class
            for cls in classes:
                sorted_keywords = sorted(sentimented_keywords[cls].items(), key=operator.itemgetter(1), reverse=True)

                # Take the top 5 keywords according to their frequency
                class_statistics[cls]['keywords'] = [keyword for keyword, frequency in sorted_keywords[:5]]

            statistics[synonym][_format_chart_date(current_time)] = {
                'sentiment': _average([snap.sentiment for snap in contained]),
                'statistics': class_statistics
            }

            current_time = current_max_time

    _append_line_exclusive('overview_timer.dat',
                           f'{_format_log_date(datetime.datetime.utcnow())}={_current_milli_time() - now_ms}')

    return statistics
