import os
import json
import logging

logger = logging.getLogger(__name__)

__version__ = '0.0.1'


def get_data_single(filePath):
    try:
        with open(filePath) as f:
            data = f.read().strip()
            if data.isdigit():
                data = int(data)
            return data
    except Exception:
        logger.exception(u'Error accessing sysfs file')
        raise


def get_data_multi(filePath):
    try:
        ret = {}
        with open(filePath) as f:
            for line in f:
                key, val = line.strip().split()
                if val.isdigit():
                    val = int(val)
                ret[key] = val
        return ret
    except Exception:
        logger.exception(u'Error accessing sysfs file')
        raise


class containerCPU(object):
    def __init__(self, containerId, sysfs='/sys',
                 cpuAcctPath='fs/cgroup/cpuacct/docker/',
                 cpuPath='fs/cgroup/cpu/docker/'):
        self.containerId = containerId
        self.cpuacct_path = os.path.join(sysfs, cpuAcctPath, str(containerId))
        self.cpu_path = os.path.join(sysfs, cpuPath, str(containerId))

        self.stats = {
            # total nanoseconds CPUs have been in use
            'usage': 0,
            # Number of enforcement intervals that have elapsed
            'nr_periods': 0,
            # Number of times the group has been throttled
            'nr_throttled': 0,
            # Total time that members of the group were throttled,
            # in nanoseconds
            'throttled_time': 0
        }

        self.__collect()

    def __collect(self):
        self.stats['usage'] = get_data_single(
            os.path.join(self.cpuacct_path, 'cpuacct.usage'))

        self.stats.update(
            get_data_multi(os.path.join(self.cpu_path, 'cpu.stat'))
        )

    def dump(self):
        return json.dumps(self.stats)


class containerMEM(object):
    def __init__(self, containerId, sysfs='/sys',
                 memPath='fs/cgroup/memory/docker/'):
        self.containerId = containerId
        self.path = os.path.join(sysfs, memPath, str(containerId))

        self.stats = {
            # Total memory used in bytes: cached + rss
            'usage': 0,
            # Total memory used + swap in use in bytes
            'memsw_usage': 0,
            # Number of times memory usage hit limits
            'failcnt': 0,
            # Memory limit of the cgroup in bytes
            'limit': 0
        }

        self.__collect()

    def __collect(self):
        self.stats['usage'] = get_data_single(
            os.path.join(self.path, 'memory.usage_in_bytes'))
        self.stats['memsw_usage'] = get_data_single(
            os.path.join(self.path, 'memory.memsw.usage_in_bytes'))
        self.stats['failcnt'] = get_data_single(
            os.path.join(self.path, 'memory.failcnt'))
        self.stats['limit'] = get_data_single(
            os.path.join(self.path, 'memory.limit_in_bytes'))
        # If number is too high, limit is not set at all
        if self.stats['limit'] > 1099511627776:
            self.stats['limit'] = 0

    def dump(self):
        return json.dumps(self.stats)


class containerMetrics(object):
    def __init__(self, containerId, sysfs='/sys'):
        self.containerId = containerId
        self.sysfs = sysfs
        self.stats = {}

        self.__collect()

    def __collect(self):
        cpu = containerCPU(containerId=self.containerId, sysfs=self.sysfs)

        mem = containerMEM(containerId=self.containerId, sysfs=self.sysfs)

        self.stats = {
            'cpu': cpu.stats,
            'mem': mem.stats
        }

    def dump(self):
        return json.dumps(self.stats)
