# docker-metrics

Python module implementing cpu, mem, i/o, net metrics extraction from pseudo-files.  

## Install

The latest version [is available on PyPI](https://pypi.python.org/pypi/docker-metrics).

With `pip`:

    pip3 install docker-metrics


## Usage

```python
#!/usr/bin/env python3

from dockermetrics import containerMetrics

metrics = containerMetrics(
    containerId='dfdd89db269a423ddd716070e8c2d85348a64703e95423608bb1b50c98057c31',
)
print(metrics.stats)
print(metrics.dump)
```

```python
#!/usr/bin/env python3

from dockermetrics import containerCPU, containerMEM

cpu = containerCPU(
     containerId='dfdd89db269a423ddd716070e8c2d85348a64703e95423608bb1b50c98057c31',
)
mem = containerMEM(
     containerId='dfdd89db269a423ddd716070e8c2d85348a64703e95423608bb1b50c98057c31',
)

print(cpu.stats)
print(mem.stats)

```

To look for sysfs in another dir:

```python
#!/usr/bin/env python3
containerMetrics(
  containerId='...',
  sysfs='/mySysFsDir'
)
```
