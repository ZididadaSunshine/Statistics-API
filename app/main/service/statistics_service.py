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

            # Compute the average sentiment
            average_sentiment = average([snap.sentiment for snap in contained])

            if contained:
                # Get which classes the snapshots agree on
                for i in contained:
                    print(i.statistics.keys())
                classes = reduce(lambda x, y: x.statistics.keys() & y.statistics.keys(), contained)
                print(classes)

                sentimented_keywords = {}
                for snap in contained:
                    for cls in classes:
                        sentimented_keywords[cls] = {}
                        # Group keywords by their sentiment. Aggregate their frequency.
                        print(snap.statistics[cls])
                        for keyword in snap.statistics[cls]['keywords']:
                            if keyword in sentimented_keywords[cls]:
                                sentimented_keywords[cls][keyword] += 1
                            else:
                                sentimented_keywords[cls][keyword] = 1

                print(sentimented_keywords)

                # Prepare the result.
                # The value of each sentiment class is a list of the keywords with the top-5
                # highest frequency.

                # Start by sorting the key/value pairs of each sentiment class
                for cls in classes:
                    for keyword_dict in sentimented_keywords[cls]:
                        sorted_keywords = sorted(keyword_dict.items(), key=operator.itemgetter(1))
                        sentimented_keywords[cls] = [word for word, score in sorted_keywords[:5]]

                print(sentimented_keywords)

            statistics[synonym][format_chart_date(current_time)] = {
                'sentiment': average_sentiment,
            }

            current_time = current_max_time

    return statistics
