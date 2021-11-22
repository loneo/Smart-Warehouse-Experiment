import csv
import datetime
import json
import math
import random

import requests as requests

address = 'http://169.56.76.12/api/message/'
order_address = 'http://169.56.76.12/api/order/'
order_total = 20
order_delay = 0
anomaly_mtbf = 2


def generate_anomaly(is_real=True, name=None):
    anomalies = []
    for i in range(3):
        if not is_real or i == 0 or i == 2:
            anomaly = []
            count = 1
            tick = 1
            while tick < order_total * 100:
                prob = 1 - math.e ** (-count / anomaly_mtbf ** 2)
                if random.random() < prob:
                    anomaly.append(tick)
                    count = 0

                count += 1
                tick += 1

            anomaly.sort()
            anomalies.append(anomaly)
        else:
            anomalies.append([])

    if name is not None:
        with open('log/anomaly/' + name + '.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for i in range(3):
                for anomaly in anomalies[i]:
                    csv_writer.writerow([anomaly, i])

    return anomalies


def generate_order_list(name=None):
    ans = []
    for i in range(order_total):
        ans.append(i % 4 + 1)

    if name is not None:
        with open('log/order/' + name + '.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for i in range(len(ans)):
                csv_writer.writerow([i + order_delay, ans[i]])

    return ans

if __name__ == "__main__":
    experiment_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    order_list = generate_order_list()
    anomalies = generate_anomaly(is_real=True, name=experiment_name)

    # experiment_name = '2021-11-20-21-58-27'
    # anomalies = [[], [], []]
    # with open('log/anomaly/' + experiment_name + '.csv', 'r', newline='') as csv_file:
    #     reader = csv.reader(csv_file)
    #     data = list(reader)
    #
    #     for single_data in data:
    #         if int(single_data[1]) == 0:
    #             anomalies[0].append(int(single_data[0]))
    #         else:
    #             anomalies[2].append(int(single_data[0]))


    # Experiment Start
    # AD-RL
    start_message = {'sender': 0,
                     'title': "Start",
                     'msg':
                         json.dumps({
                             "experiment_type": "SAS",
                             "dm_type": "AD-RL"
                         })
                     }
    requests.post(address, data=start_message)

    # ORL
    # start_message = {'sender': 0,
    #                  'title': "Start",
    #                  'msg':
    #                      json.dumps({
    #                          "experiment_type": "SAS",
    #                          "dm_type": "ORL"
    #                      })
    #                  }
    # requests.post(address, data=start_message)

    # Random
    # start_message = {'sender': 0,
    #                  'title': "Start",
    #                  'msg':
    #                      json.dumps({
    #                          "experiment_type": "SAS",
    #                          "dm_type": "Random"
    #                      })
    #                  }
    # requests.post(address, data=start_message)
    print("STARTED")

    tick = 0
    tried = [0] * 3
    while True:
        input()
        anomalies[0].append(1000000)
        anomalies[2].append(1000000)
        process_message = {
            'sender': 0,
            'title': 'Process',
            'msg': json.dumps({
                'anomaly_0': 1 if tried[0] == anomalies[0] else 0,
                'anomaly_2': 1 if tried[2] == anomalies[2] else 0
            })
        }
        res = requests.post(address, data=process_message)
        result = res.json()

        if int(result['tried_0']) == 1:
            tried[0] += 1
        if int(result['tried_2']) == 1:
            tried[2] += 1

        print('tick: ', result['tick'])
        print(result)

        if 'alert' in result.keys():
            break

        order_message = {
            'item_type': order_list[tick],
            'dest': random.randrange(3)
        }
        requests.post(order_address, data=order_message)
        tick += 1

