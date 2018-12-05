import operator

from app.main.model.snapshot_model import Snapshot
from app.main.model.synonym_model import Synonym


def average(lst):
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


def get_from_range(spans_from, spans_to, granularity, synonym):
    snapshots = Snapshot.query.select_from(Synonym).filter_by(synonym=synonym).join(Synonym.snapshots).\
        filter((Snapshot.spans_from >= spans_from) & (Snapshot.spans_to <= spans_to)).all()

    current_time = spans_from
    statistics = dict()
    while current_time < spans_to:
        current_max_time = current_time + granularity

        # Determine which snapshots are contained in the current time range
        contained = [snap for snap in snapshots if in_range(snap, current_time, current_max_time)]

        avg_sentiment = average([snap.sentiment for snap in contained])
        sentimented_keywords = {} 

        for snap in contained: 
            for sent_class in snap.statistics.keys(): 
                sentimented_keywords[sent_class] = {}
                # Group keywords by their sentiment. Aggregate their frequency. 
                for keyword, freq in snap.statistics[sent_class].items(): 
                    if keyword in sentimented_keywords[sent_class]: 
                        sentimented_keywords[sent_class][keyword] += freq 
                    else: 
                        sentimented_keywords[sent_class][keyword] = freq 

        # Prepare the result.
        # The value of each sentiment class is a list of the keywords with the top-5 
        # highest frequency. 

        # Start by sorting the key/value pairs of each sentiment class 
        for sent_class in snap.statistics.keys(): 
            for keyword_dict in sentimented_keywords[sent_class]: 
                sorted_keywords = sorted(keyword_dict.items(), key=operator.itemgetter(1))
                sentimented_keywords[sent_class] = [word for word, score in sorted_keywords[:5]]

        statistics[current_time] = {
            'sentiment' : avg_sentiment, 
            'synonym' : synonym, 
            'sentimented_keywords' : sentimented_keywords
        }

        current_time = current_max_time

    return statistics
