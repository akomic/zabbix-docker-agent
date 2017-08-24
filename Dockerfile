FROM python:3.6.0-slim

LABEL maintainer "Alen Komic <akomic@gmail.com>"

ADD zabbixAgentd zabbixDockerDiscovery setup.py setup.cfg README.txt dockerDiscovery.json.example /app/

ADD ZabbixDockerAgent /app/ZabbixDockerAgent/

RUN apt-get -q update && apt-get -y install git && \
  pip install "git+https://github.com/akomic/python-protobix.git@dev" && \
  cd /app && python setup.py build && python setup.py install

CMD ["zabbixAgentd"]
