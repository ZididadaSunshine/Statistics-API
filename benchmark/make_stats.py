import datetime

import matplotlib.pyplot as plt

ISO_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
DIVISOR = 3


def read_stats(file):
    stats = {}
    earliest_date = None

    with open(file, 'r') as o:
        for line in o.readlines():
            date, value = line.strip().split('=')

            value = float(value)
            date = datetime.datetime.strptime(date, ISO_FORMAT).replace(microsecond=0)

            if not earliest_date:
                earliest_date = date

            time_since_earliest = round((date - earliest_date).total_seconds() / DIVISOR)
            stats.setdefault(time_since_earliest, []).append(value)

    return stats


def dict_to_avg(dict):
    x = list()
    y = list()

    for key, value in dict.items():
        x.append(key * DIVISOR)
        y.append(sum(value) / len(value))

    return x, y


if __name__ == "__main__":
    response  = read_stats('response_times.dat')
    overview  = read_stats('overview_timer.dat')
    snapshot  = read_stats('snapshot_timer.dat')
    consumers = read_stats('concurrent_consumers.dat')

    resp_x, resp_y = dict_to_avg(response)
    snap_x, snap_y = dict_to_avg(snapshot)
    over_x, over_y = dict_to_avg(overview)
    cons_x, cons_y = dict_to_avg(consumers)

    if len(cons_x) < len(over_x):
        remaining = over_x[len(cons_x)-len(over_x):]
        print(remaining)
        for val in remaining:
            cons_x.append(val)
            cons_y.append(cons_y[-1])

    fig, ax1 = plt.subplots()
    fig.set_figwidth(10)
    fig.set_figheight(5)
    ln1 = ax1.plot(resp_x, resp_y, color='green', label='Response time')
    ln2 = ax1.plot(snap_x, snap_y, color='orange', label='RDMS query time')
    ln3 = ax1.plot(over_x, over_y, color='blue', label='Processing time')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Time (milliseconds)')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Consumers')
    ln4 = ax2.plot(cons_x, cons_y, color='black', label='Consumers')

    lns = ln1 + ln2 + ln3 + ln4
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=0)

    plt.title('Performance over time')
    plt.grid()
    plt.show()
