import datetime

import matplotlib.pyplot as plt
from numpy import median, mean
ISO_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
DIVISOR = 7


def read_stats(file, x_conversion=None, count=False):
    stats = {}
    earliest_date = None

    with open(file, 'r') as o:
        for line in o.readlines():
            date, value = line.strip().split('=')

            value = float(value)
            date = datetime.datetime.strptime(date, ISO_FORMAT).replace(microsecond=0)

            if not earliest_date:
                earliest_date = date

            x = round((date - earliest_date).total_seconds() / DIVISOR)

            if x_conversion:
                if x in x_conversion:
                    x = mean(x_conversion[x])
                else:
                    values = [max(item) for item in x_conversion.values()]

                    x = max(values)

            stats.setdefault(int(x), []).append(value)

    if count:
        keys = stats.keys()

        stats = {x: len(stats[x])/DIVISOR for x in keys}

    return stats


def dict_to_avg(dict):
    x = list()
    y = list()

    for key, value in dict.items():
        x.append(key)
        y.append(median(value))

    return x, y


if __name__ == "__main__":
    consumers = read_stats('concurrent_consumers.dat')

    # need to convert consumer to time
    # how much time did each consumer class exist

    response  = read_stats('response_times.dat', consumers)
    requests  = read_stats('response_times.dat', consumers, count=True)
    overview  = read_stats('overview_timer.dat', consumers)
    snapshot  = read_stats('snapshot_timer.dat', consumers)

    resp_x, resp_y = dict_to_avg(response)
    print(list(zip(resp_x, resp_y)))
    snap_x, snap_y = dict_to_avg(snapshot)
    over_x, over_y = dict_to_avg(overview)
    reqs_x, reqs_y = list(requests.keys())[:-1], list(requests.values())[:-1]

    print(reqs_y)
    fig, ax1 = plt.subplots()
    fig.set_figwidth(10)
    fig.set_figheight(5)
    ln1 = ax1.plot(resp_x, resp_y, color='green', label='Response time')
    ln2 = ax1.plot(snap_x, snap_y, color='orange', label='RDMS query time')
    ln3 = ax1.plot(over_x, over_y, color='blue', label='Processing time')
    plt.legend(bbox_to_anchor=(1.1, 1), loc=1, borderaxespad=0.)
    ax1.set_xlabel('Concurrent consumers')
    ax1.set_ylabel('Time (milliseconds)')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Requests/sec.')
    ln4 = ax2.plot(reqs_x, reqs_y, color='red', label='Requests per second')

    lns = ln1 + ln2 + ln3 + ln4
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=2)

    #plt.title('Performance with increasing consumers (1 node)')
    plt.grid(linestyle=':')
    plt.show()
    fig.savefig("statistics_two_nodes.pdf", bbox_inches='tight')
