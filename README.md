# zabbix-docker-agent

This is the implementation of Zabbix Agent specifically for dynamic nature of Docker container monitoring and it works in active mode only,
It's using two methods of collecting data from Docker, over the Docker Daemon API and through sysfs.

Tested and developed on Zabbix 3.2

NOTICE: This is not replacement for standard Zabbix Agent.

# How it works

To start monitoring you need to do the following:

- Go to: Configuration > Actions > Event Source: Auto Registration > Create Action
- Under Action tab create "New condition" with "Host metadata" like "ECSInstance"
- Under Operations tab create "Operations", "Operation type" is "Link to template" and "Templates" is "Template Docker Instance"
- Add

Running Zabbix Docker Agent on any instance will auto-create Host in Zabbix with Discovery rule which creates new Hosts in Zabbix for each discovered Docker container.
It also puts discovered Docker container hosts to groups based on Docker labels specified in configuration of the Zabbix Docker Agent.
Docker container hosts that are no longer running are removed from Zabbix automatically.

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

It needs to be mounted inside agent container under /cgroupfs (e.g. -v /cgroup:/cgroupfs or -v /sys/fs/cgroup:/cgroupfs).

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
docker run -d --restart always --name zabbixAgent \
-e DOCKERHOST=$(curl -s http://169.254.169.254/latest/meta-data/instance-id) \
-e ZBX_SERVER_HOST=zabbix-server.foo.bar \
-v /cgroup:/cgroupfs \
-v /var/run/docker.sock:/var/run/docker.sock \
akomic/zabbix-docker-agent:0.0.11
```

# Testing metrics collecting
```shell
docker exec -it zabbixAgent zabbixAgentd -t
```
