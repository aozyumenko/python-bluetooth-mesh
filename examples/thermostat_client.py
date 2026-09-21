#!/usr/bin/python3

import os
import logging
import asyncio
from typing import Union
from contextlib import suppress
from uuid import UUID
from docopt import docopt
from datetime import datetime

from bluetooth_mesh.utils import ParsedMeshMessage
from bluetooth_mesh.messages.config import GATTNamespaceDescriptor
from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode
from bluetooth_mesh.messages.generic.level import GenericLevelOpcode
from bluetooth_mesh.messages.vendor.thermostat import ThermostatOpcode
from bluetooth_mesh.models import HealthClient
from bluetooth_mesh.models.generic.onoff import GenericOnOffClient
from bluetooth_mesh.models.generic.level import GenericLevelClient
from bluetooth_mesh.models.sensor import SensorClient
from bluetooth_mesh.models.scene import SceneClient
from bluetooth_mesh.models.vendor.thermostat import ThermostatClient
from bluetooth_mesh.application import Application, Element, Capabilities


G_SEND_INTERVAL = 0.5
G_TIMEOUT = 10
G_PATH = "/ru/stdio/vendor_thermostat_" + os.environ['USER']

log = logging.getLogger()


class MainElement(Element):
    LOCATION = GATTNamespaceDescriptor.MAIN
    MODELS = [
        HealthClient,
        GenericOnOffClient,
        GenericLevelClient,
        SceneClient,
        SensorClient,
        ThermostatClient,
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

    def display_numeric(self, type: str, number: int):
        print("request key, number: %d" % (number))

    async def mesh_join(self):
        print("Join start...")
        token = await self.join()
        print("Join complete, token: 0x%x" % (token))

    async def mesh_leave(self):
        await self.connect()
        await self.leave()

    async def get(self, app_index, arguments):
        addr = int(arguments['-a'], 16)

        await self.connect()

        client = self.elements[0][ThermostatClient]
        result = await client.get(addr,
                                  app_index=app_index,
                                  send_interval=G_SEND_INTERVAL,
                                  timeout=G_TIMEOUT)
        print(result)

    async def set(self, app_index, arguments):
        addr = int(arguments['-a'], 16)
        onoff = int(arguments['<onoff>'])
        mode = int(arguments['<mode>'])
        temperature = float(arguments['<temperature>'])

        await self.connect()

        client = self.elements[0][ThermostatClient]
        result = await client.set(addr,
                                  app_index=app_index,
                                  onoff=onoff,
                                  mode=mode,
                                  temperature=temperature,
                                  send_interval=G_SEND_INTERVAL,
                                  timeout=G_TIMEOUT)
        print(result)

    async def range_get(self, app_index, arguments):
        addr = int(arguments['-a'], 16)

        await self.connect()

        client = self.elements[0][ThermostatClient]
        result = await client.range_get(addr,
                                        app_index=app_index,
                                        send_interval=G_SEND_INTERVAL,
                                        timeout=G_TIMEOUT)
        print(result)

    async def listen(self, app_index, arguments):
        def receive_status(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            now = datetime.now()
            print(f"{now}: receive {_source:04x}->{_destination:04x}")
            print(message)

        await self.connect()

        client = self.elements[0][GenericOnOffClient]
        client.app_message_callbacks[GenericOnOffOpcode.GENERIC_ONOFF_STATUS].add(receive_status)

        client = self.elements[0][GenericLevelClient]
        client.app_message_callbacks[GenericLevelOpcode.GENERIC_LEVEL_STATUS].add(receive_status)

        client = self.elements[0][ThermostatClient]
        client.app_message_callbacks[ThermostatOpcode.VENDOR_THERMOSTAT].add(receive_status)

        while True:
            await asyncio.sleep(10)

    async def run(self, app_index, cmd, arguments):
        async with self:
            if cmd == "join":
                await self.mesh_join()
            elif cmd == "leave":
                await self.mesh_leave()
            elif cmd == "get":
                await self.get(app_index, arguments)
            elif cmd == "set":
                await self.set(app_index, arguments)
            elif cmd == "range_get":
                await self.range_get(app_index, arguments)
            elif cmd == "listen":
                await self.listen(app_index, arguments)


def main():
    doc = """
    Custom Thermostat Client sample application

    Usage:
        thermostat_client.py [-V] join
        thermostat_client.py [-V] leave
        thermostat_client.py [-V] -a <address> get
        thermostat_client.py [-V] -a <address> set <onoff> <mode> <temperature>
        thermostat_client.py [-V] -a <address> range_get
        thermostat_client.py [-V] listen

    Options:
        join                    Join to the Mesh network
        leave                   Leave the Mesh network
        get                     Get Thermostat status
        set                     Set Thermostat parameters
        range_get               Get target temperature range
        -V                      Show verbose messages
        -a <address>            Local node unicast address
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)

    app_index = 0
    cmd = None

    if arguments['join']:
        cmd = "join"
    elif arguments['leave']:
        cmd = "leave"
    elif arguments['get']:
        cmd = "get"
    elif arguments['set']:
        cmd = "set"
    elif arguments['range_get']:
        cmd = "range_get"
    elif arguments["listen"]:
        cmd = "listen"
    else:
        print(doc)
        exit(-1)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(app_index, cmd, arguments))


if __name__ == '__main__':
    main()
