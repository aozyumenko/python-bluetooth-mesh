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
from bluetooth_mesh.messages.health import HealthOpcode
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


G_SEND_INTERVAL = 0.05
G_TIMEOUT = 0.2
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
    PATH = G_PATH


    async def fault_get(self, addr, app_index, arguments):
        client = self.elements[0][HealthClient]
        company_id = int(arguments['<company_id>'], 16)
        result = await client.fault_get(addr, app_index=app_index,
                                        company_id=company_id,
                                        send_interval=G_SEND_INTERVAL,
                                        timeout=G_TIMEOUT)
        print(result)

    async def fault_clear(self, addr, app_index, arguments):
        client = self.elements[0][HealthClient]
        company_id = int(arguments['<company_id>'], 16)
        result = await client.fault_clear(addr, app_index=app_index,
                                          company_id=company_id,
                                          send_interval=G_SEND_INTERVAL,
                                          timeout=G_TIMEOUT)
        print(result)

    async def fault_clear_unack(self, addr, app_index, arguments):
        client = self.elements[0][HealthClient]
        company_id = int(arguments['<company_id>'], 16)
        await client.fault_clear_unack(addr, app_index=app_index,
                                       company_id=company_id,
                                       send_interval=G_SEND_INTERVAL,
                                       retransmissions=G_UNACK_RETRANSMISSIONS)


    async def fault_test(self, addr, app_index, arguments):
        client = self.elements[0][HealthClient]
        test_id = int(arguments['<test_id>'])
        company_id = int(arguments['<company_id>'], 16)
        result = await client.fault_test(addr, app_index=app_index,
                                         test_id=test_id,
                                         company_id=company_id,
                                         send_interval=G_SEND_INTERVAL,
                                         timeout=G_TIMEOUT)
        print(result)

    async def fault_test_unack(self, addr, app_index, arguments):
        client = self.elements[0][HealthClient]
        test_id = int(arguments['<test_id>'])
        company_id = int(arguments['<company_id>'], 16)
        await client.fault_test_unack(addr, app_index=app_index,
                                      test_id=test_id,
                                      company_id=company_id,
                                      send_interval=G_SEND_INTERVAL,
                                      retransmissions=G_UNACK_RETRANSMISSIONS)


    async def period_get(self, addr, app_index, arguments):
        client = self.elements[0][HealthClient]
        result = await client.period_get(addr, app_index=app_index,
                                         send_interval=G_SEND_INTERVAL,
                                         timeout=G_TIMEOUT)
        print(result)

    async def period_set(self, addr, app_index, arguments):
        client = self.elements[0][HealthClient]
        divisor = int(arguments['<divisor>'])
        result = await client.period_set(addr, app_index=app_index,
                                         fast_period_divisor=divisor,
                                         send_interval=G_SEND_INTERVAL,
                                         timeout=G_TIMEOUT)
        print(result)

    async def period_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][HealthClient]
        divisor = int(arguments['<divisor>'])
        await client.period_set_unack(addr, app_index=app_index,
                                      fast_period_divisor=divisor,
                                      send_interval=G_SEND_INTERVAL,
                                      retransmissions=G_UNACK_RETRANSMISSIONS)

    async def attention_get(self, addr, app_index, arguments):
        client = self.elements[0][HealthClient]
        result = await client.attention_get(addr, app_index=app_index,
                                            send_interval=G_SEND_INTERVAL,
                                            timeout=G_TIMEOUT)
        print(result)

    async def attention_set(self, addr, app_index, arguments):
        client = self.elements[0][HealthClient]
        time = int(arguments['<time>'])
        result = await client.attention_set(addr, app_index=app_index,
                                            attention=time,
                                            send_interval=G_SEND_INTERVAL,
                                            timeout=G_TIMEOUT)
        print(result)

    async def attention_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][HealthClient]
        time = int(arguments['<time>'])
        await client.attention_set_unack(addr, app_index=app_index,
                                         attention=time,
                                         send_interval=G_SEND_INTERVAL,
                                         retransmissions=G_UNACK_RETRANSMISSIONS)

    async def listen(self):
        def receive_status(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            print("receive %04x->%04x" % (_source, _destination))
            print(message)

        client = self.elements[0][HealthClient]
        client.app_message_callbacks[HealthOpcode.HEALTH_CURRENT_STATUS].add(receive_status)

        while True:
            await asyncio.sleep(10)


    async def run(self, addr, app_index, cmd, arguments):
        async with self:
            await self.connect()

            if cmd == "fault_get":
                await self.fault_get(addr, app_index, arguments)
            elif cmd == "fault_clear":
                await self.fault_clear(addr, app_index, arguments)
            elif cmd == "fault_clear_unack":
                await self.fault_clear_unack(addr, app_index, arguments)
            elif cmd == "fault_test":
                await self.fault_test(addr, app_index, arguments)
            elif cmd == "fault_test_unack":
                await self.fault_test_unack(addr, app_index, arguments)
            elif cmd == "period_get":
                await self.period_get(addr, app_index, arguments)
            elif cmd == "period_set":
                await self.period_set(addr, app_index, arguments)
            elif cmd == "period_set_unack":
                await self.period_set_unack(addr, app_index, arguments)
            elif cmd == "attention_get":
                await self.attention_get(addr, app_index, arguments)
            elif cmd == "attention_set":
                await self.attention_set(addr, app_index, arguments)
            elif cmd == "attention_set_unack":
                await self.attention_set_unack(addr, app_index, arguments)
            elif cmd == "listen":
                await self.listen()


def main():
    doc = """
    Health Client Sample Application

    Usage:
        health_client.py [-V] -a <address> fault_get <company_id>
        health_client.py [-V] -a <address> fault_clear <company_id>
        health_client.py [-V] -a <address> fault_clear_unack <company_id>
        health_client.py [-V] -a <address> fault_test <test_id> <company_id>
        health_client.py [-V] -a <address> fault_test_unack <test_id> <company_id>
        health_client.py [-V] -a <address> period_get
        health_client.py [-V] -a <address> period_set <divisor>
        health_client.py [-V] -a <address> period_set_unack <divisor>
        health_client.py [-V] -a <address> attention_get
        health_client.py [-V] -a <address> attention_set <time>
        health_client.py [-V] -a <address> attention_set_unack <time>
        health_client.py [-V] listen
        health_client.py [-h | --help]
        health_client.py --version

    Options:
        -a <address>            Local node unicast address
        <company_id>            Compaty ID in hex
        <divisor>               Fast Period Divisor
        <time>                  Attention time, s
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)

    if arguments['-a']:
        addr = int(arguments['-a'], 16)
    elif arguments['listen']:
        addr = None
    else:
        print(doc)
        exit(-1)

    app_index = 0
    cmd = None

    if arguments['fault_get']:
        cmd = 'fault_get'
    elif arguments['fault_clear']:
        cmd = 'fault_clear'
    elif arguments['fault_clear_unack']:
        cmd = 'fault_clear_unack'
    elif arguments['fault_test']:
        cmd = 'fault_test'
    elif arguments['fault_test_unack']:
        cmd = 'fault_test_unack'
    elif arguments['period_get']:
        cmd = 'period_get'
    elif arguments['period_set']:
        cmd = 'period_set'
    elif arguments['period_set_unack']:
        cmd = 'period_set_unack'
    elif arguments['attention_get']:
        cmd = 'attention_get'
    elif arguments['attention_set']:
        cmd = 'attention_set'
    elif arguments['attention_set_unack']:
        cmd = 'attention_set_unack'
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
