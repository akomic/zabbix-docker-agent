FROM python:3.6.0-slim

LABEL maintainer "Alen Komic <akomic@gmail.com>"

ADD zabbixAgentd setup.py setup.cfg README.txt /app/

ADD ZabbixDockerAgent /app/ZabbixDockerAgent/

RUN cd /app && python setup.py build && python setup.py install

CMD ["zabbixAgentd"]
