# zabbix-docker-agent

This is the implementation of Zabbix Agent specifically for dynamic nature of Docker container monitoring and it works in active mode only.
It's not intended as replacement for standard Zabbix Agent.
It's using two methods of collecting data from Docker, over the Docker Daemon API and through sysfs.

# How it works

To start monitoring you need to have Server Instance added to Zabbix and 'Template Docker Instance' attached to it.
This is used by Zabbix Docker Agent to discover containers running on this instance and
place it into the already created groups that match the "CLUSTER_LABEL" and "SERVICE_LABEL" Docker labels specified in configuration.
When starting Zabbix Docker Agent DOCKERHOST needs to match the hostname specified in Zabbix.
Containers that no longer are running on the instance are removed from the Zabbix automatically.

# Configuration

All of the configuration is passed to Zabbix Docker Agent (agent) through environment variables.
Two other things beside required env variables is sysfs cgroups directory and Docker Daemon socket which needs to be mounted as volume.

On some Linux systems required pseudo file system is located in /cgroup (e.g. AWS ECS) while on the other it might be in /sys/fs/cgroup/.

```shell
$ ls /cgroup/
blkio  cpu  cpuacct  cpuset  devices  freezer  hugetlb  memory  perf_even
```

```shell
$ ls /sys/fs/cgroup/
blkio/      cpu/        cpuacct/    cpuset/     devices/    freezer/    hugetlb/    memory/     net_cls/    net_prio/   perf_event/ pids/
```

It should be mounted inside agent container under /cgroupfs (e.g. -v /cgroup:/cgroupfs or -v /sys/fs/cgroup:/cgroupfs).

## Available environment variables

| First Header    | Required | Default                                  | Description                                        |
| --------------- | -------- | ---------------------------------------- | -------------------------------------------------- |
| DOCKERHOST      | Yes      |                                          | Hostname used on Zabbix server for Docker Instance |
| ZBX_SERVER_HOST | Yes      |                                          |                                                    |
| ZBX_SERVER_PORT | No       | 10051                                    |                                                    |
| HOSTMETADATA    | No       | ECSInstance                              |                                                    |
| MAX_WORKERS     | No       | 5                                        |                                                    |
| CGROUPS_DIR     | No       | /cgroupfs                                | Directory where cgroup fs is mounted in container  |
| CLUSTER_LABEL   | No       | com.amazonaws.ecs.cluster                |                                                    |
| SERVICE_LABEL   | No       | com.amazonaws.ecs.task-definition-family |                                                    |
| LOGLEVEL        | No       | INFO                                     | CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET      |

# Running

Easiest way to run the Zabbix Docker Agent is to start it as a container on the server instance that you want to monitor.

```shell
docker run -it --rm --name zabbixAgent \
-e DOCKERHOST=$(curl -s http://169.254.169.254/latest/meta-data/instance-id) \
-e ZBX_SERVER_HOST=zabbix-server.foo.bar \
-e ZBX_SERVER_PORT=10051 \
-v /cgroup:/cgroupfs \
-v /var/run/docker.sock:/var/run/docker.sock \
akomic/zabbix-docker-agent:0.0.6 /bin/bash
```
