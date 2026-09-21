#!/usr/bin/python3

import os
import logging
import asyncio
from contextlib import suppress
from uuid import UUID
from typing import (Union)
from collections import OrderedDict
from docopt import docopt

from bluetooth_mesh.utils import ParsedMeshMessage
from bluetooth_mesh.application import Application, Element, Capabilities
from bluetooth_mesh.messages.config import GATTNamespaceDescriptor
from bluetooth_mesh.messages.scene import SceneOpcode, SceneStatusCode
from bluetooth_mesh.models.scene import SceneServer, SceneSetupServer


G_PATH = "/ru/stdio/scene_server_" + os.environ['USER']

log = logging.getLogger()


class SceneRecallDuplicateFilter:
    """ Checks whether the packet is a duplicate. """

    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self._cache = OrderedDict()

    def is_duplicate(self, source: int, tid: int) -> bool:
        key = (source, tid)

        if key in self._cache:
            self._cache.move_to_end(key)
            return True

        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)

        self._cache[key] = True
        return False


class MainElement(Element):
    LOCATION = GATTNamespaceDescriptor.MAIN
    MODELS = [
        SceneServer,
        SceneSetupServer
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

    scene_filter = SceneRecallDuplicateFilter()
    scene_number = 0
    scenes = set()

    def display_numeric(self, type: str, number: int):
        print("request key, number: %d" % (number))

    async def mesh_join(self):
        print("Join start...")
        await self.join()

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
            server = self.elements[0][SceneServer]
            self.loop.create_task(
                server.scene_status(
                    _source,
                    _app_index,
                    SceneStatusCode.SUCCESS,
                    self.scene_number
                )
            )

        def receive_recall(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            data = message.scene_recall
            if not self.scene_filter.is_duplicate(_source, data.tid):
                if data.scene_number in self.scenes:
                    self.scene_number = data.scene_number
                    status_code = SceneStatusCode.SUCCESS
                else:
                    status_code = SceneStatusCode.SCENE_NOT_FOUND

                server = self.elements[0][SceneServer]
                self.loop.create_task(
                    server.scene_status(
                        _source,
                        _app_index,
                        status_code,
                        self.scene_number
                    )
                )

        def receive_recall_unack(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            data = message.scene_recall_unacknowledged
            if not self.scene_filter.is_duplicate(_source, data.tid):
                print(f"receive {_source:04x}->{_destination:04x}: {message.scene_recall}")
                print(message.scene_recall_unacknowledged)

                if data.scene_number in self.scenes:
                    self.scene_number = data.scene_number

        def receive_register_get(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            print(f"receive {_source:04x}->{_destination:04x}: {message.scene_register_get}")

            server = self.elements[0][SceneServer]
            self.loop.create_task(
                server.scene_register_status(
                    _source,
                    _app_index,
                    SceneStatusCode.SUCCESS,
                    self.scene_number,
                    self.scenes
                )
            )

        def receive_store(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            data = message.scene_store
            print(f"receive {_source:04x}->{_destination:04x}: {data}")

            if data.scene_number > 0:
                self.scenes.add(data.scene_number)
                self.scene_number = data.scene_number
                status_code = SceneStatusCode.SUCCESS
            else:
                status_code = SceneStatusCode.SCENE_NOT_FOUND

            server = self.elements[0][SceneSetupServer]
            self.loop.create_task(
                server.scene_register_status(
                    _source,
                    _app_index,
                    status_code,
                    self.scene_number,
                    self.scenes
                )
            )

        def receive_store_unack(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            data = message.scene_store_unacknowledged
            print(f"receive {_source:04x}->{_destination:04x}: {data}")

            if data.scene_number > 0:
                self.scenes.add(data.scene_number)
                self.scene_number = data.scene_number

        def receive_delete(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            data = message.scene_delete
            print(f"receive {_source:04x}->{_destination:04x}: {data}")

            try:
                self.scenes.remove(data.scene_number)
                if (self.scene_number == data.scene_number):
                    self.scene_number = 0
                status_code = SceneStatusCode.SUCCESS
            except KeyError:
                status_code = SceneStatusCode.SCENE_NOT_FOUND

            server = self.elements[0][SceneSetupServer]
            self.loop.create_task(
                server.scene_register_status(
                    _source,
                    _app_index,
                    status_code,
                    self.scene_number,
                    self.scenes
                )
            )

        def receive_delete_unack(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            data = message.scene_delete_unacknowledged
            print(f"receive {_source:04x}->{_destination:04x}: {data}")

            self.scenes.discard(data.scene_number)
            if (self.scene_number == data.scene_number):
                self.scene_number = 0

        await self.connect()

        server = self.elements[0][SceneServer]
        server.app_message_callbacks[SceneOpcode.SCENE_GET].add(receive_get)
        server.app_message_callbacks[SceneOpcode.SCENE_RECALL].add(receive_recall)
        server.app_message_callbacks[SceneOpcode.SCENE_RECALL_UNACKNOWLEDGED].add(receive_recall_unack)
        server.app_message_callbacks[SceneOpcode.SCENE_REGISTER_GET].add(receive_register_get)

        server = self.elements[0][SceneSetupServer]
        server.app_message_callbacks[SceneOpcode.SCENE_STORE].add(receive_store)
        server.app_message_callbacks[SceneOpcode.SCENE_STORE_UNACKNOWLEDGED].add(receive_store_unack)
        server.app_message_callbacks[SceneOpcode.SCENE_DELETE].add(receive_delete)
        server.app_message_callbacks[SceneOpcode.SCENE_DELETE_UNACKNOWLEDGED].add(receive_delete_unack)

        while True:
            await asyncio.sleep(10)

    async def run(self, cmd, arguments):
        async with self:
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
        scene_server.py [-V] join
        scene_server.py [-V] leave
        scene_server.py [-V]
        scene_server.py [-h | --help]
        scene_server.py --version

    Options:
        join                    join to the Mesh network
        leave                   leave the Mesh network
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = SampleApplication(loop)

    if arguments['join']:
        cmd = "join"
    elif arguments['leave']:
        cmd = "leave"
    else:
        cmd = "start"

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(cmd, arguments))


if __name__ == '__main__':
    main()
