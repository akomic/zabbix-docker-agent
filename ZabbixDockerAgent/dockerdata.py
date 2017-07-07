import docker

from dockermetrics import containerMetrics


class dockerData(object):
    def __init__(self,
                 clusterLabel='com.amazonaws.ecs.cluster',
                 serviceLabel='com.docker.compose.project'):
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
        return containerMetrics(containerId=containerId, sysfs='/sysfs')
