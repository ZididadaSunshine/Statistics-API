import datetime
import fcntl

from locust import HttpLocust, TaskSet, task, events
from random import randint, sample, randrange

USER_CREDENTIALS = list()
WORDS = [line.strip() for line in open('../words.txt')][:500]
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
EARLIEST = datetime.datetime(day=11, month=12, year=2017)
LATEST = datetime.datetime(day=11, month=12, year=2018)

consumer_count = 0


def _random_date():
    delta = LATEST - EARLIEST
    return EARLIEST + datetime.timedelta(seconds=randint(0, delta.total_seconds() / 1.5))


def _random_range(min_time, max_days):
    start = _random_date()
    min_seconds = min_time.total_seconds()
    max_seconds = max_days.total_seconds()
    end = start + datetime.timedelta(seconds=randint(min_seconds, max_seconds))

    return start, end


def _format_log_date():
    return datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%d %H:%M:%S.%f')


def _append_line_exclusive(file, contents):
    with open(file, 'a') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        file.write(contents + '\n')
        fcntl.flock(file, fcntl.LOCK_UN)


def _log_response_time(request_type, name, response_time, response_length):
    _append_line_exclusive('response_times.dat', f'{_format_log_date()}={response_time}')


events.request_success += _log_response_time


class ConsumerBehavior(TaskSet):
    def on_start(self):
        global consumer_count
        consumer_count += 1
        _append_line_exclusive('concurrent_consumers.dat', f'{_format_log_date()}={consumer_count}')

    def _request(self, granularity, spans_from, spans_to):
        request_data = {
            'from': spans_from.strftime(ISO_FORMAT),
            'to': spans_to.strftime(ISO_FORMAT),
            'synonyms': sample(WORDS, randint(1, 3))
        }

        self.client.post(f'/statistics/{granularity}/overview', json=request_data)

    @task(1)
    def request_hour(self):
        spans_from, spans_to = _random_range(datetime.timedelta(hours=1), datetime.timedelta(days=1))

        self._request('hour', spans_from, spans_to)

    @task(2)
    def request_half_day(self):
        spans_from, spans_to = _random_range(datetime.timedelta(hours=12), datetime.timedelta(days=14))

        self._request('halfday', spans_from, spans_to)

    @task(3)
    def request_day(self):
        spans_from, spans_to = _random_range(datetime.timedelta(days=1), datetime.timedelta(days=31))

        self._request('day', spans_from, spans_to)

    @task(4)
    def request_week(self):
        spans_from, spans_to = _random_range(datetime.timedelta(days=7), datetime.timedelta(days=62))

        self._request('week', spans_from, spans_to)


class StatisticsConsumer(HttpLocust):
    task_set = ConsumerBehavior
    min_wait = 5000
    max_wait = 10000
