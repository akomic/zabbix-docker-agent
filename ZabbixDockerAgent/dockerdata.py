import os
import docker

from .toolbox import AppError
from dockermetrics import containerMetrics


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

        self.docker = docker.from_env()
        self.containers = {}
        self.discoveryData = []

    def discover_containers(self):
        for container in self.docker.containers.list():
            self.discoveryData.append({
                '{#CONTAINER_NAME}': container.name,
                '{#CONTAINER_ID}': container.id,
                '{#CONTAINER_STATUS}': container.status,
                '{#CONTAINER_CLUSTER}':
                    container.labels.get(self.clusterLabel),
                '{#CONTAINER_SERVICE}':
                    container.labels.get(self.serviceLabel)
            })
            self.containers[container.id] = {
                'name': container.name,
                'short_id': container.short_id,
                'status': container.status,
                'labels': container.labels
            }

    def metrics(self, containerId):
        try:
            return containerMetrics(
                containerId=containerId,
                sysfs=os.getenv('CGROUPS_DIR', '/cgroupsfs')
            )
        except Exception as e:
            raise AppError(str(e))
