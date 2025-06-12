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
from bluetooth_mesh.messages.generic.battery import (
    GenericBatteryFlagsPresence,
    GenericBatteryFlagsIndicator,
    GenericBatteryFlagsCharging,
    GenericBatteryFlagsServiceability,
)
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


G_SEND_INTERVAL = 0.1
G_TIMEOUT = 10.0
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
        client = self.elements[0][GenericBatteryClient]
        result = await client.get(addr, app_index=app_index,
                                  send_interval=G_SEND_INTERVAL,
                                  timeout=G_TIMEOUT)
        print(result)


    async def listen(self, addr, app_index, arguments):
        def receive_status(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            print("receive %04x->%04x" % (_source, _destination))
            print(message)

        client = self.elements[0][GenericBatteryClient]
        client.app_message_callbacks[GenericBatteryOpcode.GENERIC_BATTERY_STATUS].add(receive_status)

        while True:
            await asyncio.sleep(10)


    async def run(self, addr, app_index, cmd, arguments):
        async with self:
            await self.connect()

            if cmd == "get":
                await self.get(addr, app_index, arguments)
            elif cmd == "listen":
                await self.listen(addr, app_index, arguments)


def main():
    doc = """
    Generic Battery Client Sample Application

    Usage:
        generic_battery_client.py [-V] -a <address> get
        generic_battery_client.py [-V] -a <address> listen
        generic_battery_client.py [-h | --help]
        generic_battery_client.py --version

    Options:
        -a <address>            Local node unicast address
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
