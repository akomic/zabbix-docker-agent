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
            return self.raw['Name'].strip('/')
        except Exception:
            return ''

    def __get2(self, key1, key2, ret=''):
        try:
            return self.raw[key1][key2]
        except Exception:
            return ret

    def getLabel(self, labelName):
        try:
            return self.info['labels'][labelName]
        except Exception:
            return ''

    def get(self, key, ret=''):
        if key in self.info:
            return self.info[key]
        else:
            return ret

    def __process(self):
        self.info = {
            'name': self.__getName(),
            'id': self.raw['Id'],
            'short_id': self.raw['Id'][0:12],
            'status': self.__get2('State', 'Status'),
            'labels': self.__get2('Config', 'Labels', {}),
            'image': self.__get2('Config', 'Image'),
            'restartCount': self.raw.get('RestartCount', 0),
            'cpuShares': self.__get2('HostConfig', 'CpuShares', 0),
            'memory': self.__get2('HostConfig', 'Memory', 0),
            'memoryReservation': self.__get2('HostConfig',
                                             'memoryReservation', 0),
            'memorySwap': self.__get2('HostConfig', 'MemorySwap', 0)
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
                '{#CONTAINER_CLUSTER}': container.getLabel(self.clusterLabel),
                '{#CONTAINER_SERVICE}': container.getLabel(self.serviceLabel),
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
