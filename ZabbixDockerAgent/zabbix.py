import os
import protobix
import logging

from .toolbox import AppError
from zabbixactivechecks import ItemList


class Zabbix(object):
    def __init__(self):
        self.logProtobix = logging.getLogger('Protobix')
        self.zbx_config = protobix.ZabbixAgentConfig()
        self.zbx_config.server_active = os.getenv('ZBX_SERVER_HOST')
        self.zbx_config.server_port = \
            int(os.getenv('ZBX_SERVER_PORT', '10051'))
        self.zbx_config.timeout = 10

        self.zbx_datacontainer = None

    def initSender(self, dataType='items'):
        self.zbx_config.data_type = dataType
        self.zbx_datacontainer = protobix.DataContainer(config=self.zbx_config)
        return self.zbx_datacontainer

    def getItemList(self, host, hostMetadata=None):
        try:
            list = ItemList(host=host)
            response = list.get(
                server=self.zbx_config.server_active,
                port=self.zbx_config.server_port,
                hostMetadata=hostMetadata
            )
            return response.data
        except Exception as e:
            raise AppError(str(e))
