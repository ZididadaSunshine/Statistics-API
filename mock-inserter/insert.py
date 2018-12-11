import datetime
import json
import random
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor


import requests

ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

CLASSES = {'negative', 'positive'}

NUM_SYNONYMS = 500
WORDS = [line.strip() for line in open('words.txt')][:NUM_SYNONYMS]

TIME_DELTA = datetime.timedelta(hours=1)
END_DATE = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
START_DATE = END_DATE - datetime.timedelta(days=365)

ENDPOINT = 'http://172.28.198.101:8013/api/snapshots'


def insert_snapshot(spans_from, spans_to, synonym):
    try:
        snapshot = {
            'synonym': synonym,
            'from': spans_from.strftime(ISO_FORMAT),
            'to': spans_to.strftime(ISO_FORMAT),
            'sentiment': random.uniform(0, 1)
        }

        statistics = dict()
        for cls in CLASSES:
            statistics[cls] = {
                'posts': random.randint(0, 1000),
                'keywords': random.sample(WORDS, 10)
            }

        snapshot['statistics'] = json.dumps(statistics)

        response = requests.post(ENDPOINT, json=snapshot)
        if response.status_code not in {409, 201}:
            print(response.status_code)
            print(response.text)
    except Exception as ex:
        print(ex)

        insert_snapshot(spans_from, spans_to, synonym)


def insert_range(from_range, to_range, synonym):
    current_time = from_range

    while current_time < to_range:
        next_time = current_time + TIME_DELTA

        insert_snapshot(current_time, next_time, synonym)

        current_time = next_time

    print(synonym + ' finished')


if __name__ == "__main__":
    synonyms = WORDS.copy()

    jobs = []
    with ThreadPoolExecutor(max_workers=500) as executor:
        while synonyms:
            jobs.append(executor.submit(insert_range, START_DATE, END_DATE, synonyms.pop()))

    futures.wait(jobs)
