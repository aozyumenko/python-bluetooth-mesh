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
from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode
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


G_SEND_INTERVAL = 0.5
G_TIMEOUT = 3
G_UNACK_RETRANSMISSIONS = 3
G_JSON_CONF = "join_client_" + os.environ['USER'] +".json"


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

    @property
    def iv_index(self):
        return 0

    def token_load(self):
        try:
            with open(G_JSON_CONF, "r") as tokenfile:
                try:
                    return json.load(tokenfile)
                except (json.JSONDecodeError, EOFError):
                    return dict({'user': os.environ['USER'], 'token': None, 'path': self.PATH})
        except FileNotFoundError:
            return dict({'user': os.environ['USER'], 'token': None, 'path': self.PATH})


    async def get(self, addr, app_index, arguments):
        client = self.elements[0][GenericOnOffClient]
        result = await client.get([addr], app_index=app_index,
                                  send_interval=G_SEND_INTERVAL,
                                  timeout=G_TIMEOUT)
        print(result[addr])

    async def set(self, addr, app_index, arguments):
        client = self.elements[0][GenericOnOffClient]
        val = int(arguments['<val>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.set([addr], app_index=app_index,
                                  onoff=val,
                                  transition_time=transition_time,
                                  send_interval=G_SEND_INTERVAL,
                                  timeout=G_TIMEOUT)
        print(result[addr])

    async def set_unack(self, addr, app_index, arguments):
        client = self.elements[0][GenericOnOffClient]
        val = int(arguments['<val>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.set_unack(addr, app_index=app_index,
                               onoff=val,
                               transition_time=transition_time,
                               send_interval=G_SEND_INTERVAL,
                               retransmissions=G_UNACK_RETRANSMISSIONS)


    async def listen(self, addr, app_index, arguments):
        def receive_status(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            print("receive %04x->%04x" % (_source, _destination))
            print(message)

        client = self.elements[0][GenericOnOffClient]
        client.app_message_callbacks[GenericOnOffOpcode.GENERIC_ONOFF_STATUS].add(receive_status)

        while True:
            await asyncio.sleep(10)


    async def run(self, addr, app_index, cmd, arguments):
        async with self:
            token_conf = self.token_load()
            if 'token' in token_conf:
                self.token_ring.token = token_conf['token']
            if 'path' in token_conf:
                self.PATH = token_conf['path']

            await self.connect()

            if cmd == "get":
                await self.get(addr, app_index, arguments)
            elif cmd == "set":
                await self.set(addr, app_index, arguments)
            elif cmd == "set_unack":
                await self.set_unack(addr, app_index, arguments)
            elif cmd == "listen":
                await self.listen(addr, app_index, arguments)


def main():
    doc = """
    Generic On/Off Client Sample Application

    Usage:
        generic_onoff_client.py [-V] -a <address> get
        generic_onoff_client.py [-V] -a <address> [--transition=<time>] set <val>
        generic_onoff_client.py [-V] -a <address> [--transition=<time>] set_unack <val>
        generic_onoff_client.py [-V] -a <address> listen
        generic_onoff_client.py [-h | --help]
        generic_onoff_client.py --version

    Options:
        -a <address>            Local node unicast address
        <val>                   0-off, 1-on
        --transition=<time>     Transition time
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)

    addr = int(arguments['-a'], 16)
    app_index = 0
    cmd = None

    if arguments['get']:
        cmd = 'get'
    elif arguments['set']:
        cmd = 'set'
    elif arguments['set_unack']:
        cmd = 'set_unack'
    elif arguments['listen']:
        cmd = 'listen'
    else:
        print(doc)
        exit(-1)

    loop = asyncio.get_event_loop()
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(addr, app_index, cmd, arguments))


if __name__ == '__main__':
    main()
