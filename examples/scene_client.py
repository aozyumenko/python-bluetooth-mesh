#!/usr/bin/python3

import os
import logging
import asyncio
import secrets
from contextlib import suppress
from uuid import UUID

from docopt import docopt

from bluetooth_mesh.application import Application, Element, Capabilities
from bluetooth_mesh.crypto import ApplicationKey, DeviceKey, NetworkKey
from bluetooth_mesh.messages.config import GATTNamespaceDescriptor, StatusCode
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
        SceneClient,
        GenericLevelClient,
        GenericBatteryClient,
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
    PATH = G_PATH


    async def get(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        result = await client.get(addr, app_index=app_index)
        print(result)

    async def recall(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else None
        result = await client.recall(
            addr,
            app_index=app_index,
            scene_number=scene_number,
            transition_time=transition_time
        )
        print(result)

    async def recall_unack(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else None
        await client.recall_unack(
            addr,
            app_index=app_index,
            scene_number=scene_number,
            transition_time=transition_time
        )

    async def register_get(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        result = await client.register_get(addr, app_index=app_index)
        print(result)

    async def store(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        result = await client.store(
            addr,
            app_index=app_index,
            scene_number=scene_number
        )
        print(result)

    async def store_unack(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        await client.store_unack(
            addr,
            app_index=app_index,
            scene_number=scene_number
        )

    async def delete(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        result = await client.delete(
            addr,
            app_index=app_index,
            scene_number=scene_number
        )
        print(result)

    async def delete_unack(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        await client.delete_unack(
            addr,
            app_index=app_index,
            scene_number=scene_number
        )


    async def run(self, addr, app_index, cmd, arguments):
        async with self:
            await self.connect()

            if cmd == "get":
                await self.get(addr, app_index, arguments)
            elif cmd == "recall":
                await self.recall(addr, app_index, arguments)
            elif cmd == "recall_unack":
                await self.recall_unack(addr, app_index, arguments)
            elif cmd == "register_get":
                await self.register_get(addr, app_index, arguments)
            elif cmd == "store":
                await self.store(addr, app_index, arguments)
            elif cmd == "store_unack":
                await self.store_unack(addr, app_index, arguments)
            elif cmd == "delete":
                await self.delete(addr, app_index, arguments)
            elif cmd == "delete_unack":
                await self.delete_unack(addr, app_index, arguments)


def main():
    doc = """
    Scene Client Sample Application

    Usage:
        scene_client.py [-V] -a <address> get
        scene_client.py [-V] -a <address> [--transition=<time>] recall <number>
        scene_client.py [-V] -a <address> [--transition=<time>] recall_unack <number>
        scene_client.py [-V] -a <address> register_get
        scene_client.py [-V] -a <address> store <number>
        scene_client.py [-V] -a <address> store_unack <number>
        scene_client.py [-V] -a <address> delete <number>
        scene_client.py [-V] -a <address> delete_unack <number>
        scene_client.py [-h | --help]
        scene_client.py --version

    Options:
        -a <address>            Local node unicast address
        <number>                Scene number
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
    elif arguments['recall']:
        cmd = 'recall'
    elif arguments['recall_unack']:
        cmd = 'recall_unack'
    elif arguments['register_get']:
        cmd = 'register_get'
    elif arguments['store']:
        cmd = 'store'
    elif arguments['store_unack']:
        cmd = 'store_unack'
    elif arguments['delete']:
        cmd = 'delete'
    elif arguments['delete_unack']:
        cmd = 'delete_unack'
    else:
        print(doc)
        exit(-1)

    addr = int(arguments['-a'], 16)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(addr, app_index, cmd, arguments))


if __name__ == '__main__':
    main()
