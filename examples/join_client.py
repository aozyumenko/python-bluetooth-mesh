#!/usr/bin/python3

import sys
import os
import asyncio
import secrets
from contextlib import suppress
from uuid import UUID
import json
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

import logging
log = logging.getLogger()


G_PATH = "/com/silvair/sample_" + os.environ['USER']


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
        return "/com/silvair/sample_" + G_PATH


    def display_string(self, value: str):
        print("request key: %s" % str)

    def display_numeric(self, type: str, number: int):
         print("request key: type=%s, number=%d" % (type, number))


    async def mesh_join(self):
        print("Starting join...")
        self.token_ring.token = await self.join()
        print("Join start, token=0x%x" % (self.token_ring.token))

    async def mesh_leave(self):
        await self.leave()

    async def run(self, arguments):
        async with self:
            if arguments['-l']:
                # LEAVE
                await self.mesh_leave()
            else:
                # JOIN
                await self.mesh_join()

def main():
    doc = """
    Join client node Sample Application

    Usage:
        join_client.py [-V]
        join_client.py [-V] -l
        join_client.py [-h | --help]
        join_client.py --version

    Options:
        -l                      Leave node
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        path_suffix = os.environ['USER']

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(arguments))



if __name__ == '__main__':
    main()
