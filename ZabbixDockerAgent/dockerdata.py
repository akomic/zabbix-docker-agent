import os
import docker

from .toolbox import AppError
from dockermetrics import containerMetrics


class Container(object):
    def __init__(self, container):
        self.raw = container

        self.info = {}

        self.__process()

    def __getName(self):
        try:
            return (self.raw['Name'].strip('/'), 0)
        except KeyError:
            return ('Unknown key', 1)
        except Exception as e:
            return (repr(e), 1)

    def __getShortId(self):
        try:
            return (self.raw['Id'][0:12], 0)
        except KeyError:
            return ('Unknown key', 1)
        except Exception as e:
            return (repr(e), 1)

    def __get(self, key1, key2=None):
        try:
            if key2 is None:
                return (self.raw[key1], 0)
            else:
                return (self.raw[key1][key2], 0)
        except KeyError:
            return ('Unknown key ' + key1 + ' ' + key2, 1)
        except Exception as e:
            return (repr(e), 1)

    def getLabel(self, labelName, ret=''):
        try:
            return self.info['labels'][0][labelName]
        except Exception:
            return ret

    def get(self, key, ret=''):
        if key in self.info and self.info[key][1] == 0:
            return self.info[key][0]
        else:
            return ret

    def __process(self):
        self.info = {
            'name': self.__getName(),
            'id': self.__get('Id'),
            'short_id': self.__getShortId(),
            'status': self.__get('State', 'Status'),
            'labels': self.__get('Config', 'Labels'),
            'image': self.__get('Config', 'Image'),
            'restartCount': self.__get('RestartCount'),
            'cpuShares': self.__get('HostConfig', 'CpuShares'),
            'memory': self.__get('HostConfig', 'Memory'),
            'memoryReservation': self.__get('HostConfig', 'MemoryReservation'),
            'memorySwap': self.__get('HostConfig', 'MemorySwap')
        }


class Containers(object):
    def __init__(self):
        self.docker = docker.APIClient(base_url='unix://var/run/docker.sock')

    def __iter__(self):
        for c in self.docker.containers():
            inspectData = self.docker.inspect_container(c['Id'])
            container = Container(inspectData)
            yield container


class dockerData(object):
    def __init__(self):
        labels = os.getenv('LABELS','')
        self.labels = [l.strip() for l in labels.split(',')]

        self.containers = {}
        self.instancesData = {}

    def discover_containers(self):
        for container in Containers():
            self.containers[container.get('id')] = container.info
            self.instancesData[container.get('id')] = {
                'short_id': container.get('short_id'),
                'name': container.get('name'),
                'groups': list(
                    set(
                        ['Containers'] +
                        [
                            container.getLabel(l, 'Containers')
                            for l in self.labels
                        ]
                    )
                )
            }

    def metrics(self, containerId):
        try:
            metrics = containerMetrics(
                containerId=containerId,
                sysfs=os.getenv('CGROUPS_DIR', '/cgroupfs')
            )

            ret = metrics.stats
            ret['info'] = self.containers[containerId]
            return ret
        except Exception as e:
            raise AppError(str(e))
