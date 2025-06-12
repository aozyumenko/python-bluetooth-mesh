#!/usr/bin/python3

import os
import logging
import asyncio
import secrets
from contextlib import suppress
from uuid import UUID
import json
from typing import (Union)

from docopt import docopt

from bluetooth_mesh.utils import ParsedMeshMessage
from bluetooth_mesh.application import Application, Element, Capabilities
from bluetooth_mesh.crypto import ApplicationKey, DeviceKey, NetworkKey
from bluetooth_mesh.messages.config import GATTNamespaceDescriptor, StatusCode
from bluetooth_mesh.messages.generic.level import GenericLevelOpcode
from bluetooth_mesh.models import (
    ConfigClient,
    HealthClient,
)
from bluetooth_mesh.models.generic.onoff import GenericOnOffClient
from bluetooth_mesh.models.generic.level import GenericLevelClient
from bluetooth_mesh.models.generic.dtt import GenericDTTClient
from bluetooth_mesh.models.generic.ponoff import GenericPowerOnOffClient
from bluetooth_mesh.models.generic.battery import GenericBatteryClient
from bluetooth_mesh.models.sensor import SensorClient
from bluetooth_mesh.models.time import TimeClient
from bluetooth_mesh.models.scene import SceneClient
from bluetooth_mesh.models.light.lightness import LightLightnessClient
from bluetooth_mesh.models.light.ctl import LightCTLClient
from bluetooth_mesh.models.light.hsl import LightHSLClient


G_SEND_INTERVAL = 0.5
G_TIMEOUT = 3
G_UNACK_RETRANSMISSIONS = 3
G_PATH = "/com/silvair/sample_" + os.environ['USER']


log = logging.getLogger()


class MainElement(Element):
    LOCATION = GATTNamespaceDescriptor.MAIN
    MODELS = [
        ConfigClient,
        HealthClient,
        GenericOnOffClient,
        GenericDTTClient,
        GenericPowerOnOffClient,
        GenericBatteryClient,
        SceneClient,
        GenericLevelClient,
        SensorClient,
        LightLightnessClient,
        LightCTLClient,
        LightHSLClient,
        TimeClient,
    ]


class SampleApplication(Application):
    COMPANY_ID = 0x0136  # Silvair
    PRODUCT_ID = 0x0001
    VERSION_ID = 1
    ELEMENTS = {
        0: MainElement,
    }
    CAPABILITIES = [Capabilities.OUT_NUMERIC]

    CRPL = 32768


    @property
    def path(self) -> str:
        return G_PATH


    async def get(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        result = await client.get(addr, app_index=app_index,
                                  send_interval=G_SEND_INTERVAL,
                                  timeout=G_TIMEOUT)
        print(result)

    async def set(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.set(addr, app_index=app_index,
                                  level=level,
                                  transition_time=transition_time,
                                  send_interval=G_SEND_INTERVAL,
                                  timeout=G_TIMEOUT)
        print(result)

    async def set_unack(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.set_unack(addr, app_index=app_index,
                               level=level,
                               transition_time=transition_time,
                               retransmissions=G_UNACK_RETRANSMISSIONS,
                               send_interval=G_SEND_INTERVAL)

    async def delta_set(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.delta_set(addr, app_index=app_index,
                                        delta_level=level,
                                        transition_time=transition_time,
                                        send_interval=G_SEND_INTERVAL,
                                        timeout=G_TIMEOUT)
        print(result)

    async def delta_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.delta_set_unack(addr, app_index=app_index,
                                     delta_level=level,
                                     transition_time=transition_time,
                                     retransmissions=G_UNACK_RETRANSMISSIONS,
                                     send_interval=G_SEND_INTERVAL)

    async def move_set(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.move_set(addr, app_index=app_index,
                                       delta_level=level,
                                       transition_time=transition_time,
                                       send_interval=G_SEND_INTERVAL,
                                       timeout=G_TIMEOUT)
        print(result)

    async def move_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.move_set_unack(addr, app_index=app_index,
                                    delta_level=level,
                                    transition_time=transition_time,
                                    retransmissions=G_UNACK_RETRANSMISSIONS,
                                    send_interval=G_SEND_INTERVAL)

    async def listen(self, addr, app_index, arguments):
        def receive_status(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            print("receive %04x->%04x" % (_source, _destination))
            print(message)

        client = self.elements[0][GenericLevelClient]
        client.app_message_callbacks[GenericLevelOpcode.GENERIC_LEVEL_STATUS].add(receive_status)

        while True:
            await asyncio.sleep(10)


    async def run(self, addr, app_index, cmd, arguments):
        async with self:
            await self.connect()

            if cmd == "get":
                await self.get(addr, app_index, arguments)
            elif cmd == "set":
                await self.set(addr, app_index, arguments)
            elif cmd == "set_unack":
                await self.set_unack(addr, app_index, arguments)
            elif cmd == "delta_set":
                await self.delta_set(addr, app_index, arguments)
            elif cmd == "delta_set_unack":
                await self.delta_set_unack(addr, app_index, arguments)
            elif cmd == "move_set":
                await self.move_set(addr, app_index, arguments)
            elif cmd == "move_set_unack":
                await self.move_set_unack(addr, app_index, arguments)
            elif cmd == "listen":
                await self.listen(addr, app_index, arguments)


def main():
    doc = """
    Generic Level Client Sample Application

    Usage:
        generic_level_client.py [-V] -a <address> get
        generic_level_client.py [-V] -a <address> [--transition=<time>] set <level>
        generic_level_client.py [-V] -a <address> [--transition=<time>] set_unack <level>
        generic_level_client.py [-V] -a <address> [--transition=<time>] delta_set <level>
        generic_level_client.py [-V] -a <address> [--transition=<time>] delta_set_unack <level>
        generic_level_client.py [-V] -a <address> [--transition=<time>] move_set <level>
        generic_level_client.py [-V] -a <address> [--transition=<time>] move_set_unack <level>
        generic_level_client.py [-V] -a <address> listen
        generic_level_client.py [-h | --help]
        generic_level_client.py --version

    Options:
        -a <address>            Local node unicast address
        <level>                 Level value: 0-32768 to 32767
        --transition=<time>     Transition time
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)

    if arguments['-a']:
        addr = int(arguments['-a'], 16)
    else:
        print(doc)
        exit(-1)

    app_index = 0
    cmd = None

    if arguments['get']:
        cmd = 'get'
    elif arguments['set']:
        cmd = 'set'
    elif arguments['set_unack']:
        cmd = 'set_unack'
    elif arguments['delta_set']:
        cmd = 'delta_set'
    elif arguments['delta_set_unack']:
        cmd = 'delta_set_unack'
    elif arguments['move_set']:
        cmd = 'move_set'
    elif arguments['move_set_unack']:
        cmd = 'move_set_unack'
    elif arguments['listen']:
        cmd = 'listen'
    else:
        print(doc)
        exit(-1)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(addr, app_index, cmd, arguments))


if __name__ == '__main__':
    main()
