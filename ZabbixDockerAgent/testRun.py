import json
from ZabbixDockerAgent import dockerData


class TestRun(object):
    def __init__(self):
        self.collect_metrics()

    def collect_metrics(self):
        dckr = dockerData()

        dckr.discover_containers()

        info = {}
        for containerId in dckr.containers:
            data = dckr.metrics(containerId)
            info[containerId] = data

        print(json.dumps(dckr.instancesData))
        print(json.dumps(info))
