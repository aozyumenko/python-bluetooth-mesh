#!/usr/bin/python3

import os
import logging
import asyncio
import secrets
from contextlib import suppress
from uuid import UUID
from typing import (Union)
import time
from datetime import datetime, timedelta, timezone

from docopt import docopt

from bluetooth_mesh.utils import ParsedMeshMessage
from bluetooth_mesh.application import Application, Element, Capabilities
from bluetooth_mesh.crypto import ApplicationKey, DeviceKey, NetworkKey
from bluetooth_mesh.messages.properties import PropertyID
from bluetooth_mesh.messages.config import GATTNamespaceDescriptor, StatusCode
from bluetooth_mesh.messages.time import CURRENT_TAI_UTC_DELTA
from bluetooth_mesh.models import ConfigClient, HealthClient
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


G_TIMEOUT = 5

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
    PATH = "/com/silvair/sample_" + os.environ['USER']

    @property
    def iv_index(self):
        return 0


    async def get(self, addr, app_index, arguments):
        client = self.elements[0][TimeClient]
        result = await client.get(
            [addr],
            app_index=app_index,
            timeout=G_TIMEOUT
        )
        print(result[addr])

    async def time_zone_get(self, addr, app_index, arguments):
        client = self.elements[0][TimeClient]
        result = await client.time_zone_get(
            [addr],
            app_index=app_index,
            timeout=G_TIMEOUT
        )
        print(result[addr])

    async def tai_utc_delta_get(self, addr, app_index, arguments):
        client = self.elements[0][TimeClient]
        result = await client.tai_utc_delta_get(
            [addr],
            app_index=app_index,
            timeout=G_TIMEOUT
        )
        print(result[addr])

    async def set(self, addr, app_index, arguments):
        system_timezone_offset = time.timezone * -1
        system_timezone = timezone(offset=timedelta(seconds=system_timezone_offset))
        date = datetime.now(system_timezone)

        client = self.elements[0][TimeClient]
        result = await client.set(
            [addr],
            app_index=app_index,
            date=date,
            tai_utc_delta=timedelta(seconds=CURRENT_TAI_UTC_DELTA),
            uncertainty=timedelta(0),
            time_authority=True,
            timeout=G_TIMEOUT
        )
        print(result[addr])



    async def run(self, token, addr, app_index, cmd, arguments):
        async with self:
            self.token_ring.token = token

            await self.connect()

            if cmd == "get":
                await self.get(addr, app_index, arguments)
            elif cmd == "time_zone_get":
                await self.time_zone_get(addr, app_index, arguments)
            elif cmd == "tai_utc_delta_get":
                await self.tai_utc_delta_get(addr, app_index, arguments)
            elif cmd == "set":
                await self.set(addr, app_index, arguments)



def main():
    doc = """
    Time Server Sample Application

    Usage:
        time_server.py [-V] -t <token> -a <address> get
        time_server.py [-V] -t <token> -a <address> time_zone_get
        time_server.py [-V] -t <token> -a <address> tai_utc_delta_get
        time_server.py [-V] -t <token> -a <address> set
        time_server.py [-h | --help]
        time_server.py --version

    Options:
        -t <token>              bluetooth-meshd node token
        -a <address>            Local node unicast address
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)

    token = int(arguments['-t'], 16)
    addr = int(arguments['-a'], 16)
    app_index = 0
    cmd = None

    if arguments['get']:
        cmd = 'get'
    elif arguments['time_zone_get']:
        cmd = 'time_zone_get'
    elif arguments['tai_utc_delta_get']:
        cmd = 'tai_utc_delta_get'
    elif arguments['set']:
        cmd = 'set'
    else:
        print(doc)
        exit(-1)

    loop = asyncio.get_event_loop()
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(token, addr, app_index, cmd, arguments))


if __name__ == '__main__':
    main()
