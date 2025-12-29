#!/usr/bin/python3

import os
import sys
import logging
import asyncio
import secrets
from contextlib import suppress
from uuid import UUID
import yaml
from typing import (Union)
from datetime import datetime
from construct import Container

from docopt import docopt

from bluetooth_mesh.utils import ParsedMeshMessage
from bluetooth_mesh.application import Application, Element, Capabilities
from bluetooth_mesh.crypto import ApplicationKey, DeviceKey, NetworkKey
from bluetooth_mesh.messages.properties import PropertyID
from bluetooth_mesh.messages.config import GATTNamespaceDescriptor, StatusCode
from bluetooth_mesh.messages.sensor import SensorOpcode, SensorSetupOpcode
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
G_TIMEOUT = 10.0
G_PATH = "/com/silvair/sample_" + os.environ['USER']

log = logging.getLogger()



def unpack_property(prop: Container) -> dict():
    result = dict()
    for key in prop.keys():
        value = prop[key]
        if isinstance(value, dict):
            result[key] = unpack_property(value)
        else:
            result[key] = value
    return result


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


    async def descriptor_get(self, app_index, arguments):
        addr = int(arguments["-a"], 16)
        client = self.elements[0][SensorClient]
        result = await client.descriptor_get(
            addr,
            app_index=app_index,
            send_interval=G_SEND_INTERVAL,
            timeout=G_TIMEOUT
        )
        print(result)

    async def get(self, addr, app_index, arguments):
        addr = int(arguments["-a"], 16)
        client = self.elements[0][SensorClient]
        property_id = int(arguments["-p"], 16) if arguments["-p"] else None
        result = await client.get(
            addr,
            app_index=app_index,
            property_id=property_id,
            send_interval=G_SEND_INTERVAL,
            timeout=G_TIMEOUT
        )
        print(result)

    async def cadence_get(self, app_index, arguments):
        addr = int(arguments["-a"], 16)
        client = self.elements[0][SensorClient]

        if arguments["-p"]:
            property_ids = [ int(arguments["-p"], 16) ]
        else:
            desc = await client.descriptor_get(
                addr,
                app_index=app_index,
                send_interval=G_SEND_INTERVAL,
                timeout=G_TIMEOUT
            )
            property_ids = [ int(prop.sensor_property_id) for prop in desc ]

        conf = dict()
        for property_id in property_ids:
            result = await client.cadence_get(
                addr,
                app_index=app_index,
                property_id=property_id,
                send_interval=G_SEND_INTERVAL,
                timeout=G_TIMEOUT
            )

            cadence = dict()
            cadence["fast_cadence_period_divisor"] = result.fast_cadence_period_divisor
            if result.status_trigger_type == 0:
                cadence["status_trigger_type"] = "unit"
                cadence["status_trigger_delta_down"] = unpack_property(result.status_trigger_delta_down)
                cadence["status_trigger_delta_up"] = unpack_property(result.status_trigger_delta_up)
            else:
                cadence["status_trigger_type"] = "percent"
                cadence["status_trigger_delta_down"] = result.status_trigger_delta_down
                cadence["status_trigger_delta_up"] = result.status_trigger_delta_up
            cadence["status_min_interval"] = result.status_min_interval
            cadence["fast_cadence_low"] = unpack_property(result.fast_cadence_low)
            cadence["fast_cadence_high"] = unpack_property(result.fast_cadence_high)

            conf[f"{property_id:x}"] = cadence

        if arguments["<file>"]:
            with open(arguments["<file>"], "w") as file:
                yaml.dump(conf, file)
        else:
            yaml.dump(conf, sys.stdout)


    async def cadence_set(self, app_index, arguments):
        addr = int(arguments["-a"], 16)
        client = self.elements[0][SensorClient]

        with open(arguments["<file>"], "r") as file:
            conf = yaml.safe_load(file)

        print(conf)
        for (_property_id, cadence) in conf.items():
            property_id = int(_property_id, 16)
            result = await client.cadence_set(
                addr,
                app_index=app_index,
                sensor_setting_property_id=property_id,
                fast_cadence_period_divisor=cadence["fast_cadence_period_divisor"],
                status_trigger_type=(0 if cadence["status_trigger_type"] == "unit" else 1),
                status_trigger_delta_down=cadence["status_trigger_delta_down"],
                status_trigger_delta_up=cadence["status_trigger_delta_up"],
                status_min_interval=cadence["status_min_interval"],
                fast_cadence_low=cadence["fast_cadence_low"],
                fast_cadence_high=cadence["fast_cadence_high"],
                send_interval=G_SEND_INTERVAL,
                timeout=G_TIMEOUT
            )


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

        client = self.elements[0][SensorClient]
        client.app_message_callbacks[SensorOpcode.SENSOR_STATUS].add(receive_status)

        while True:
            await asyncio.sleep(10)


    async def run(self, app_index, cmd, arguments):
        async with self:
            await self.connect()

            if cmd == "descriptor_get":
                await self.descriptor_get(app_index, arguments)
            elif cmd == "cadence_get":
                await self.cadence_get(app_index, arguments)
            elif cmd == "cadence_set":
                await self.cadence_set(app_index, arguments)
            elif cmd == "get":
                await self.get(app_index, arguments)
            elif cmd == "listen":
                await self.listen(app_index, arguments)


def main():
    doc = """
    Sensor Client Sample Application

    Usage:
        sensor_client.py [-V] -a <address> descriptor_get
        sensor_client.py [-V] -a <address> [-p <property_id>] cadence_get [<file>]
        sensor_client.py [-V] -a <address> cadence_set <file>
        sensor_client.py [-V] -a <address> [-p <property_id>] get
        sensor_client.py [-V] listen
        sensor_client.py [-h | --help]
        sensor_client.py --version

    Options:
        -a <address>            Local node unicast address
        -p <property_id>        Sensor property id in hex
        <file>                  YAML file for load/store configuration
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version="1.0")

    if arguments["-V"]:
        logging.basicConfig(level=logging.DEBUG)

    app_index = 0
    cmd = None

    if arguments["descriptor_get"]:
        cmd = "descriptor_get"
    elif arguments["cadence_get"]:
        cmd = "cadence_get"
    elif arguments["cadence_set"]:
        cmd = "cadence_set"
    elif arguments["get"]:
        cmd = "get"
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
