#!/usr/bin/env python

from distutils.core import setup
# you can also import from setuptools

setup(
    name='docker-metrics',
    packages=['dockermetrics'],
    version='0.0.1',

    description='Implementation of Docker Metrics from sysfs',
    long_description=(
        'This module implements'
        ' cpu, mem, i/o, net metrics extraction from pseudo-files.\n'
    ),
    author='Alen Komic',
    author_email='akomic@gmail.com',
    license='GPL',
    url='https://github.com/akomic/docker-metrics',
    download_url='https://github.com/akomic/docker-metrics',
    keywords=['docker', 'monitoring', 'metrics'],
    classifiers=[],
)
