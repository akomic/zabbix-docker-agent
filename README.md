# zabbix-docker-agent

TBD

# Running
```shell
```

# Configuration

Available environment variables

| First Header    | Required | Default                                  |
| --------------- | -------- | ---------------------------------------- |
| DOCKERHOST      | Yes      |                                          |
| ZBX_SERVER_HOST | Yes      |                                          |
| ZBX_SERVER_PORT | Yes      |                                          |
| HOSTMETADATA    | No       | ECSInstance                              |
| MAX_WORKERS     | No       | 5                                        |
| CGROUPS_DIR     | No       | /cgroupsfs                               |
| CLUSTER_LABEL   | No       | com.amazonaws.ecs.cluster                |
| SERVICE_LABEL   | No       | com.amazonaws.ecs.task-definition-family |

# Running

```shell
docker run -it --rm --name zabbixAgent \
-e DOCKERHOST=$(curl -s http://169.254.169.254/latest/meta-data/instance-id) \
-e ZBX_SERVER_HOST=zabbix-server.foo.bar \
-e ZBX_SERVER_PORT=10051 \
-v /cgroup:/cgroupsfs \
-v /var/run/docker.sock:/var/run/docker.sock \
akomic/zabbix-docker-agent:0.0.6 /bin/bash
```
