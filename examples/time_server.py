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
from bluetooth_mesh.messages.time import TimeOpcode, TimeRole, CURRENT_TAI_UTC_DELTA
from bluetooth_mesh.models.time import TimeServer, TimeSetupServer


G_TIMEOUT = 5

log = logging.getLogger()



class MainElement(Element):
    LOCATION = GATTNamespaceDescriptor.MAIN
    MODELS = [
        TimeServer,
        TimeSetupServer
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
    PATH = "/com/silvair/sample_time_server"

    @property
    def iv_index(self):
        return 0

    def display_numeric(self, type: str, number: int):
         print("request key, number: %d" % (number))

    async def mesh_join(self):
        print("Join start...")
        token = await self.join()
        print("Join complete, token: 0x%x" % (token))

    async def mesh_leave(self):
        await self.connect()
        await self.leave()

    async def mesh_listen(self):
        def receive_get(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            print("Get: receive %04x->%04x" % (_source, _destination))

            system_timezone_offset = time.timezone * -1
            system_timezone = timezone(offset=timedelta(seconds=system_timezone_offset))
            date = datetime.now(system_timezone)

            server = self.elements[0][TimeServer]
            self.loop.create_task(
                server.time_status(
                    _source,
                    _app_index,
                    date,
                    timedelta(seconds=CURRENT_TAI_UTC_DELTA),
                    timedelta(0),
                    True
                )
            )

        def receive_time_zone_get(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            print("Time Zone Get: receive %04x->%04x" % (_source, _destination))

            system_timezone_offset = time.timezone * -1
            system_timezone_delta = timedelta(seconds=system_timezone_offset)

            server = self.elements[0][TimeServer]
            self.loop.create_task(
                server.time_zone_status(
                    _source,
                    _app_index,
                    system_timezone_delta,
                    system_timezone_delta,
                    0
                )
            )

        def receive_tai_utc_delta_get(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            print("TAI-UTC Delta Get: receive %04x->%04x" % (_source, _destination))

            server = self.elements[0][TimeServer]
            self.loop.create_task(
                server.tai_utc_delta_status(
                    _source,
                    _app_index,
                    CURRENT_TAI_UTC_DELTA,
                    CURRENT_TAI_UTC_DELTA,
                    0
                )
            )

        # Time Setup Server message handlers
        def receive_set(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            print("Get: receive %04x->%04x" % (_source, _destination))

            server = self.elements[0][TimeServer]
            self.loop.create_task(
                server.time_status(
                    _source,
                    _app_index,
                    message.time_set.date,
                    message.time_set.tai_utc_delta,
                    message.time_set.uncertainty,
                    message.time_set.time_authority,
                )
            )


        await self.connect()

        server = self.elements[0][TimeServer]
        server.app_message_callbacks[TimeOpcode.TIME_GET].add(receive_get)
        server.app_message_callbacks[TimeOpcode.TIME_ZONE_GET].add(receive_time_zone_get)
        server.app_message_callbacks[TimeOpcode.TAI_UTC_DELTA_GET].add(receive_tai_utc_delta_get)

        server = self.elements[0][TimeSetupServer]
        server.app_message_callbacks[TimeOpcode.TIME_SET].add(receive_set)

        while True:
            await asyncio.sleep(10)


    async def run(self, cmd, arguments):
        async with self:
            if arguments['-t']:
                self.token_ring.token = int(arguments['-t'], 16)

            if cmd == "join":
                await self.mesh_join()
            elif cmd == "leave":
                await self.mesh_leave()
            elif cmd == "start":
                await self.mesh_listen()



def main():
    doc = """
    Time Server Sample Application

    Usage:
        time_server.py [-V] join
        time_server.py [-V] -t <token> leave
        time_server.py [-V] -t <token>
        time_server.py [-h | --help]
        time_server.py --version

    Options:
        join                    join to the Mesh network
        -t <token>              bluetooth-meshd node token
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app = SampleApplication(loop)

    if arguments['join']:
        cmd = "join"
    elif arguments['leave']:
        cmd = "leave"
    elif arguments['-t']:
        cmd = "start"
    else:
        print(doc)
        exit(-1)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(cmd, arguments))


if __name__ == '__main__':
    main()
