#!/usr/bin/env python

from setuptools import setup

setup(
    # Application name:
    name="zabbix-docker-agent",

    # Version number (initial):
    version="0.2.0",

    # Application author details:
    author="Alen Komic",
    author_email="akomic@gmail.com",

    # Packages
    packages=["ZabbixDockerAgent"],

    # Scripts
    scripts=['zabbixAgentd','zabbixDockerDiscovery'],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/akomic/zabbix-docker-agent",

    #
    # license="LICENSE.txt",
    description="Zabbix Docker Agent for collecting dynamic" +
                " container statistics",

    long_description=open("README.txt").read(),

    keywords=['docker', 'monitoring', 'metrics', 'zabbix'],

    data_files=[('/etc/zabbix', ['dockerDiscovery.json.example'])],

    # Dependent packages (distributions)
    install_requires=[
        'docker==2.4.0', 'docker-metrics==0.0.5',
        'protobix==1.0.0rc1', 'zabbixactivechecks==0.0.5'
    ],
)
