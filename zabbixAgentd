#!/usr/bin/env python3
import os
import sys
import json
import time
import concurrent.futures

from ZabbixDockerAgent import Zabbix, dockerData


def parse_key(itemKey):
    docker, section, key = itemKey.split('.')
    return section, key


if os.getenv('DOCKERHOST') is None or \
   os.getenv('ZBX_SERVER_HOST') is None or \
   os.getenv('ZBX_SERVER_PORT') is None:
    print("Required env variables:"
          " DOCKERHOST, ZBX_SERVER_HOST, ZBX_SERVER_PORT")
    sys.exit(1)


def doInstance(dckr):
    zbx = Zabbix()
    instanceItems = zbx.getItemList(host=os.getenv('DOCKERHOST'),
                                    hostMetadata='ECSInstance')

    print(instanceItems)

    sender = zbx.initSender(dataType='lld')
    sender.add_item(os.getenv('DOCKERHOST'), 'docker.discovery',
                    dckr.discoveryData)
    sender.send()

    del zbx


def doContainer(containerId, zbx, dckr):
    print(containerId, dckr.containers[containerId]['name'])
    items = zbx.getItemList(host=containerId)
    print(json.dumps(items))
    metrics = dckr.metrics(containerId=containerId)
    print(metrics.stats)

    for item in items:
        section, key = parse_key(item['key'])
        print('ITEM:', section, key, metrics.stats[section][key])
        sender.add_item(
            containerId,
            item['key'],
            metrics.stats[section][key]
        )
    return 'YES!'


while True:
    start_time = time.time()
    dckr = dockerData()

    dckr.discover_containers()

    doInstance(dckr)

    zbx = Zabbix()

    sender = zbx.initSender(dataType='items')
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_container = {
            executor.submit(doContainer, containerId, zbx, dckr): containerId for containerId in dckr.containers}

        for future in concurrent.futures.as_completed(future_to_container):
            containerId = future_to_container[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (containerId, exc))
            else:
                print('%r page is %d bytes' % (containerId, len(data)))
    sender.send()

    del zbx
    del dckr

    sleep_time = (60 - (time.time() - start_time))

    print("Sleeping for {0}".format(sleep_time))
    time.sleep(sleep_time)
