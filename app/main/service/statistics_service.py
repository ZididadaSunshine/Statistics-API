import datetime
import operator
import time
from functools import reduce

from app.main.model.snapshot_model import Snapshot
from app.main.model.synonym_model import Synonym

_current_milli_time = lambda: int(round(time.time() * 1000))


def _format_chart_date(date):
    return datetime.datetime.strftime(date, '%Y-%m-%d %H:%M:%S')


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
    snapshots = Snapshot.query.select_from(Synonym).filter(Synonym.synonym.in_(synonyms)).join(Synonym.snapshots). \
        filter((Snapshot.spans_from >= spans_from) & (Snapshot.spans_to <= spans_to)).all()

    return snapshots


def _get_n_latest(granularity_span, synonyms, n):
    now = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    start = now - granularity_span * n

    snapshots = _get_snapshots(start, now, synonyms)

    result = []
    current_time = start
    while current_time < now:
        next_time = current_time + granularity_span

        result.append([snap for snap in snapshots if _in_range(snap, current_time, next_time)])

        current_time = next_time

    return result


def _aggregate_keywords(snapshots, skip_words=None):
    aggregated = dict()

    classes = _get_intersecting_classes(snapshots)
    aggregated_by_class = _aggregate_keywords_by_class(classes, snapshots, skip_words)
    for cls in classes:
        for keyword, frequency in aggregated_by_class[cls].items():
            aggregated[keyword] = aggregated.get(keyword, 0) + frequency

    return aggregated


def _aggregate_keywords_by_class(sentiment_classes, snapshots, skip_words=None):
    sentimented_keywords = dict()

    for cls in sentiment_classes:
        sentimented_keywords[cls] = dict()

        for snapshot in snapshots:
            for keyword in snapshot.statistics[cls]['keywords']:
                if skip_words and keyword in skip_words:
                    continue

                sentimented_keywords[cls][keyword] = sentimented_keywords[cls].get(keyword, 0) + 1

    return sentimented_keywords


def _get_intersecting_classes(snapshots):
    if snapshots:
        all_keys = [snap.statistics.keys() for snap in snapshots]

        return reduce(lambda x, y: x & y, all_keys)

    return list()


def _normalize_values(from_dict, with_min, with_max):
    return {x: (from_dict[x] - with_min) / (with_max - with_min) for x in from_dict}


def get_average(granularity_span, synonyms):
    """ Provides the combined average over all the provided synonyms. """
    # Only retrieve snapshots once and then use in_range to determine which are in the correct ranges (less queries)
    previous_snapshots, current_snapshots = _get_n_latest(granularity_span, synonyms, 2)

    # Get average sentiment values
    current_average = _average([snap.sentiment for snap in current_snapshots])
    previous_average = _average([snap.sentiment for snap in previous_snapshots])

    # Sum posts for all classes in current snapshot period
    posts = 0
    if current_snapshots:
        classes = _get_intersecting_classes(current_snapshots)
        posts = reduce(lambda x, y: _sum_posts(current_snapshots, x) + _sum_posts(current_snapshots, y), classes)

    return {
        'sentiment_average': current_average,
        'sentiment_trend': current_average - previous_average if previous_average else None,
        'posts': posts
    }


def get_overview(spans_from, spans_to, granularity, synonyms, n_keywords=5):
    """ Provides an overview for all synonyms and for each granularity that fits into it. """
    snapshots = _get_snapshots(spans_from, spans_to, synonyms)

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

            # Get the intersection of classes
            classes = _get_intersecting_classes(contained)

            # Aggregate keywords by sentiment classes
            sentimented_keywords = _aggregate_keywords_by_class(classes, contained, synonyms)

            # Sort key/value pairs of each sentiment class
            class_statistics = dict()
            for cls in classes:
                sorted_keywords = sorted(sentimented_keywords[cls].items(), key=operator.itemgetter(1), reverse=True)

                # Take the top 5 keywords according to their frequency
                class_statistics[cls] = {
                    'posts': _sum_posts(contained, cls),
                    'keywords': [keyword for keyword, frequency in sorted_keywords[:n_keywords]]
                }

            statistics[synonym][_format_chart_date(current_time)] = {
                'sentiment': _average([snap.sentiment for snap in contained]),
                'statistics': class_statistics
            }

            current_time = current_max_time

    return statistics


def get_trending_keywords(granularity_span, synonyms, n_keywords=10):
    previous, current = _get_n_latest(granularity_span, synonyms, 2)

    # Aggregate all keywords from the period
    aggregated_keywords = _aggregate_keywords(previous + current, synonyms)
    if not aggregated_keywords:
        return dict()

    # Get the minimum and maximum frequency
    min_frequency = min(aggregated_keywords.values())
    max_frequency = max(aggregated_keywords.values())

    # If min and max frequency are the same, return no keywords
    if min_frequency == max_frequency:
        return dict()

    # Aggregate keywords by granularity and normalise the values
    previous_keywords = _normalize_values(_aggregate_keywords(previous, synonyms), min_frequency, max_frequency)
    current_keywords = _normalize_values(_aggregate_keywords(current, synonyms), min_frequency, max_frequency)

    # Return the slope for each common keyword
    common_keywords = set(previous_keywords.keys()).intersection(set(current_keywords.keys()))
    slopes = {keyword: current_keywords[keyword] - previous_keywords[keyword] for keyword in common_keywords}

    # Sort keywords by slope
    sorted_keywords = sorted(slopes.items(), key=operator.itemgetter(1), reverse=True)

    return {keyword: frequency for keyword, frequency in sorted_keywords[:n_keywords]}
