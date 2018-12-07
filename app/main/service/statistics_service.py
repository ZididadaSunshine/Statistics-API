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


def in_range(snap, lower, upper):
    if snap.spans_to > upper:
        return False

    if snap.spans_from < lower:
        timespan = (snap.spans_to - snap.spans_from).seconds
        diff = (lower - snap.spans_from).seconds
        return (diff / timespan) < 0.5
    
    else: 
        return True


def get_from_range(spans_from, spans_to, granularity, synonyms):
    # In the future, multiple synonyms will be supported
    snapshots = Snapshot.query.select_from(Synonym).filter(Synonym.synonym.in_(synonyms)).join(Synonym.snapshots).\
        filter((Snapshot.spans_from >= spans_from) & (Snapshot.spans_to <= spans_to)).all()

    statistics = {synonym: dict() for synonym in synonyms}
    for synonym in synonyms:
        current_time = spans_from

        while current_time < spans_to:
            current_max_time = current_time + granularity

            # Determine which snapshots are contained in the current time range
            contained = [snap for snap in snapshots if in_range(snap, current_time, current_max_time)]

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
