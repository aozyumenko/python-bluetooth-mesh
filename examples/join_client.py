#!/usr/bin/python3

import sys
import os
import asyncio
import secrets
from contextlib import suppress
from uuid import UUID
from docopt import docopt
#from typing import Any

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
from bluetooth_mesh.models.sensor import SensorClient
from bluetooth_mesh.models.time import TimeClient
from bluetooth_mesh.models.scene import SceneClient
from bluetooth_mesh.models.light.lightness import LightLightnessClient
from bluetooth_mesh.models.light.ctl import LightCTLClient
from bluetooth_mesh.models.light.hsl import LightHSLClient

import logging
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

    def __init__(self, path_suffix, loop) -> None:
        self.PATH = "/com/silvair/sample_" + path_suffix
        super().__init__(loop)


    @property
    def iv_index(self):
        return 0

    def display_string(self, value: str):
        print("request key: %s" % str)

    def display_numeric(self, type: str, number: int):
         print("request key: type=%s, number=%d" % (type, number))


    async def mesh_join(self):
        token = await self.join()
        print("Join start, token=0x%x" % (token))

    async def mesh_leave(self, token):
        self.token_ring.token = token
        await self.leave()

    async def run(self, arguments):
        async with self:
            if arguments['-l']:
                # LEAVE
                token = int(arguments['-l'], 16)
                await self.mesh_leave(token)
            else:
                # JOIN
                await self.mesh_join()

def main():
    doc = """
    Join client node Sample Application

    Usage:
        join_client.py [-V] [-s <path suffix>]
        join_client.py [-V] -l <token>
        join_client.py [-h | --help]
        join_client.py --version

    Options:
        -s <path suffix>        Suffix for DBUS path
        -l <token>              Leave node
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)
    if arguments['-s']:
        path_suffix = arguments['-s']
    else:
        path_suffix = os.environ['USER']

    loop = asyncio.get_event_loop()
    app = SampleApplication(path_suffix, loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(arguments))



if __name__ == '__main__':
    main()
