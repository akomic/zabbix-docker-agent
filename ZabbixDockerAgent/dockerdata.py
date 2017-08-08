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
    def __init__(self,
                 clusterLabel=os.getenv(
                     'CLUSTER_LABEL',
                     'com.amazonaws.ecs.cluster'
                 ),
                 serviceLabel=os.getenv(
                     'SERVICE_LABEL',
                     'com.amazonaws.ecs.task-definition-family'
                 )):
        self.clusterLabel = clusterLabel
        self.serviceLabel = serviceLabel

        self.containers = {}
        self.discoveryData = []

    def discover_containers(self):
        for container in Containers():
            self.discoveryData.append({
                '{#CONTAINER_NAME}': container.get('name'),
                '{#CONTAINER_ID}': container.get('id'),
                '{#CONTAINER_SHORT_ID}': container.get('short_id'),
                '{#CONTAINER_STATUS}': container.get('status'),
                '{#CONTAINER_CLUSTER}': container.getLabel(
                    self.clusterLabel, 'Containers'),
                '{#CONTAINER_SERVICE}': container.getLabel(
                    self.serviceLabel, 'Containers'),
                '{#CONTAINER_IMAGE}': container.get('image'),
                '{#CONTAINER_RESTARTCOUNT}': container.get('restartCount', 0),
                '{#CONTAINER_CPUSHARES}': container.get('cpuShares', 0),
                '{#CONTAINER_MEMORY}': container.get('memory', 0),
                '{#CONTAINER_MEMORYRESERVATION}': container.get(
                    'memoryReservation', 0),
                '{#CONTAINER_MEMORYSWAP}': container.get('memorySwap', 0)
            })
            self.containers[container.get('id')] = container.info

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
