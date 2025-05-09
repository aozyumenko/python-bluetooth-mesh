#!/usr/bin/python3

import os
import logging
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
from bluetooth_mesh.models.sensor import SensorClient
from bluetooth_mesh.models.time import TimeClient
from bluetooth_mesh.models.scene import SceneClient
from bluetooth_mesh.models.vendor.thermostat import ThermostatClient


from bluetooth_mesh.messages.vendor.thermostat import (
    ThermostatOpcode,
    ThermostatSubOpcode,
)
from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode


G_SEND_INTERVAL = 0.5
G_TIMEOUT = 10
G_JSON_CONF = "thermostat_client_" + os.environ['USER'] +".json"
G_PATH = "/ru/stdio/vendor_thermostat_" + os.environ['USER']

log = logging.getLogger()




class MainElement(Element):
    LOCATION = GATTNamespaceDescriptor.MAIN
    MODELS = [
        HealthClient,
        GenericOnOffClient,
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

    def token_save(self, data):
        with open(G_JSON_CONF, "w") as tokenfile:
            return json.dump(data, tokenfile)

    def display_numeric(self, type: str, number: int):
         print("request key, number: %d" % (number))

    async def mesh_join(self, token_conf):
        print("Join start...")
        token = await self.join()
        print("Join complete, token: 0x%x" % (token))
        token_conf['token'] = token
        self.token_save(token_conf)

    async def mesh_leave(self):
        await self.connect()
        await self.leave()
        os.remove(G_JSON_CONF)

    async def get(self, arguments):
        addr = int(arguments['-a'], 16)
        app_index = 0

        await self.connect()

        client = self.elements[0][ThermostatClient]
        result = await client.get([addr],
                                  app_index=app_index,
                                  send_interval=G_SEND_INTERVAL,
                                  timeout=G_TIMEOUT)
        print(result[addr])

    async def set(self, arguments):
        addr = int(arguments['-a'], 16)
        app_index = 0
        onoff = int(arguments['<onoff>'])
        mode = int(arguments['<mode>'])
        temperature = float(arguments['<temperature>'])

        await self.connect()

        client = self.elements[0][ThermostatClient]
        result = await client.set([addr],
                                  app_index=app_index,
                                  onoff=onoff,
                                  mode=mode,
                                  temperature=temperature,
                                  send_interval=G_SEND_INTERVAL,
                                  timeout=G_TIMEOUT)
        print(result[addr])

    async def range_get(self, arguments):
        addr = int(arguments['-a'], 16)
        app_index = 0

        await self.connect()

        client = self.elements[0][ThermostatClient]
        result = await client.range_get([addr],
                                        app_index=app_index,
                                        send_interval=G_SEND_INTERVAL,
                                        timeout=G_TIMEOUT)
        print(result[addr])

    async def run(self, cmd, arguments):
        async with self:
            token_conf = self.token_load()
            if 'token' in token_conf and token_conf['token'] is not None:
                self.token_ring.token = token_conf['token']
            if 'path' in token_conf:
                self.PATH = token_conf['path']

            if cmd == "join":
                await self.mesh_join(token_conf)
            elif cmd == "leave":
                await self.mesh_leave()
            elif cmd == "get":
                await self.get(arguments);
            elif cmd == "set":
                await self.set(arguments);
            elif cmd == "range_get":
                await self.range_get(arguments);


def main():
    doc = """
    Custom Thermostat Client sample application

    Usage:
        thermostat_client.py [-V] join
        thermostat_client.py [-V] leave
        thermostat_client.py [-V] -a <address> get
        thermostat_client.py [-V] -a <address> set <onoff> <mode> <temperature>
        thermostat_client.py [-V] -a <address> range_get

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
    else:
        print(doc)
        exit(-1)

    loop = asyncio.get_event_loop()
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(cmd, arguments))


if __name__ == '__main__':
    main()
