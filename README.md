# zabbix-docker-agent

This is the implementation of Zabbix Agent specifically for dynamic nature of Docker container monitoring and it works in active mode only,
It's using two methods of collecting data from Docker, over the Docker Daemon API and through sysfs.

Tested and developed on Zabbix 3.2

NOTICE: This is not replacement for standard Zabbix Agent.

# How it works

To start monitoring you need to do the following:

- Go to: Configuration > Actions > Event Source: Auto Registration > Create Action
- Under Action tab create "New condition" with "Host metadata" like "DockerInstance"
- Under Operations tab create "Operations", "Operation type" is "Link to template" and "Templates" is "Template Docker Instance"
- Add

Running Zabbix Docker Agent on any instance will auto-create Host (Docker Instance) on Zabbix.
Zabbix-Docker-Agent is sending periodically information about all running containers which is stored base64 encoded under item "Docker Groups and Containers" key "docker.instanceDiscovery".

zabbixDockerDiscovery is responsible for digesting docker.instanceDiscovery item data and:
- Creating hosts and attaching template "Template Docker Container" in Zabbix for each discovered container on any Docker Instance running Zabbix-Docker-Agent
- Creating groups in Zabbix based on labels found on Docker Containers
- Creating Zabbix hosts and attaching template "Template Docker Group" in Zabbix for each created Zabbix group so we can have aggregate items for container groups (metrics based on container labels)
- Destroying unused/empty Zabbix groups and hosts with "Template Docker Group" attached
- Destroying Zabbix hosts with "Template Docker Container" attached that the corresponding Docker Containers are no longer found on any of the Docker Instances.

# Configuration

## Agent

Configuration is passed to Zabbix Docker Agent (agent) through environment variables.
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

### Available environment variables

| First Header    | Required | Default                                  | Description                                        |
| --------------- | -------- | ---------------------------------------- | -------------------------------------------------- |
| DOCKERHOST      | Yes      |                                          | Hostname used on Zabbix server for Docker Instance |
| ZBX_SERVER_HOST | Yes      |                                          |                                                    |
| ZBX_SERVER_PORT | No       | 10051                                    |                                                    |
| HOSTMETADATA    | No       | DockerInstance                           |                                                    |
| MAX_WORKERS     | No       | 5                                        |                                                    |
| CGROUPS_DIR     | No       | /cgroupfs                                | Directory where cgroup fs is mounted in container  |
| LABELS          | No       |                                          | Docker labels used to create Zabbix Groups         |
| LOGLEVEL        | No       | INFO                                     | CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET      |


## Discovery

- Instal zabbix-agent-docker on Zabbix server
```shell
pip3 install zabbix-docker-agent
```
- Create API user on Zabbix
- Copy example config file dockerDiscovery.json.example and edit it
- Run zabbixDockerDiscovery by crontab on Zabbix Server
```shell
*/15 * * * * /usr/local/bin/zabbixDockerDiscovery 2>&1 >/dev/null
```

# Running

Easiest way to run the Zabbix Docker Agent is to start it as a container on the server instance that you want to monitor.

```shell
docker run -d --restart always --name zabbixAgent \
-e DOCKERHOST=$(curl -s http://169.254.169.254/latest/meta-data/instance-id) \
-e ZBX_SERVER_HOST=zabbix-server.foo.bar \
-e LABELS="StackName,com.amazonaws.ecs.task-definition-family" \
-v /cgroup:/cgroupfs \
-v /var/run/docker.sock:/var/run/docker.sock \
akomic/zabbix-docker-agent:latest
```

Edit and run zabbixDockerDiscovery on Zabbix Server.

# Testing metrics collecting
```shell
docker exec -it zabbixAgent zabbixAgentd -t
```
