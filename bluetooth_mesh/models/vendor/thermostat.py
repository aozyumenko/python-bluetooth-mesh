#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2023  Alexander Ozumenko
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
"""
This module implements experemental Thermostat mesh models, both clients and servers.
"""

from functools import partial
#from typing import Any, Dict, Iterable, NamedTuple, Optional, Sequence, Tuple, Type
from typing import Any, Dict, Sequence, Optional
from enum import IntEnum        # FIXME: for base class only

from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.vendor.thermostat import (
    ThermostatOpcode,
    ThermostatSubOpcode,
)

import asyncio
from typing import Mapping, Hashable, Callable, Awaitable, Union
from uuid import UUID
from bluetooth_mesh.utils import ProgressCallback, ParsedMeshMessage, MessageDescription
from bluetooth_mesh.messages import AccessMessage

__all__ = [
    "ThermostatServer",
    "ThermostatClient",
]


class VendorModel(Model):
    """
    Base class for vendor mesh models.
    """

    def __init__(self, element: "Element"):
        self.OPCODES = { self.OPCODE };
        print(self.OPCODES)
        super().__init__(element);


    def expect_subapp(
        self,
        source: int,
        app_index: int,
        destination: Optional[Union[int, UUID]],
        subopcode: int,
        params: MessageDescription,
    ) -> asyncio.Future:
        """
        Create an `asyncio.Future` that gets fulfilled when a specific
        application vendor message is received.

        :param source: Sender address
        :param app_index: Index of the application key
        :param destination: Destination address
        :param subopcode: Expected message subopcode.
        :param params: Expected message parameters.
        """

        future = asyncio.Future()

        def app_message_received(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            if (_source != source) or (_app_index != app_index):
                return False

            if destination is not None and (_destination != destination):
                return False

            if params and not construct_match(message[self.OPCODE.name.lower()][subopcode.name.lower()], params):
                return False

            if not future.done():
                future.set_result(message[self.OPCODE.name.lower()])

            return True

        self.app_message_callbacks[self.OPCODE].add(app_message_received)

        return future


    async def send_subapp(
        self, destination: int, app_index: int, subopcode: int, params: MessageDescription
    ):
        """
        Send a vendor specific message using an application key.

        :param destination: Destination address
        :param app_index: Index of the application key
        :param subopcode: Vendor message sub opcode.
        :param params: Vendor message parameters.
        """

        data = AccessMessage.build(
            dict(
                opcode=self.OPCODE,
                params=dict(
                    subopcode=int(subopcode),
                    payload=params
                )
            )
        )

        message = AccessMessage.parse(data)
        self.logger.debug(
            "Sending: %s -> %04x [app_index %d] %r",
            self.element.path,
            destination,
            app_index,
            message,
        )

        await super()._send_app(destination, app_index, data)


    # implementation of simple client *get command
    async def client_simple_get(
        self,
        nodes: Sequence[int],
        app_index: int,
        request_subopcode: IntEnum,
        status_subopcode: IntEnum,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_subapp,
                destination=node,
                app_index=app_index,
                subopcode=request_subopcode,
                params=dict(),
            )
            for node in nodes
        }

        statuses = {
            node: self.expect_subapp(
                source=node,
                app_index=app_index,
                destination=None,
                subopcode=status_subopcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
            send_interval=send_interval,
            timeout=timeout,
        )

        return {
            node: None if isinstance(result, BaseException)
            else result[status_subopcode.name.lower()]
            for node, result in results.items()
        }


    # implementation of simple client *set vendor command
    async def client_simple_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        request_subopcode: IntEnum,
        status_subopcode: IntEnum,
        params: dict,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None,
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_subapp,
                destination=node,
                app_index=app_index,
                subopcode=request_subopcode,
                params=params,
            )
            for node in nodes
        }

        statuses = {
            node: self.expect_subapp(
                source=node,
                app_index=app_index,
                destination=None,
                subopcode=status_subopcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
            send_interval=send_interval,
            timeout=timeout,
        )

        return {
            node: None if isinstance(result, BaseException)
            else result[status_subopcode.name.lower()]
            for node, result in results.items()
        }



class ThermostatServer(Model):
    MODEL_ID = (0x0005, 0x0000)
    OPCODES = {
        ThermostatOpcode.VENDOR_THERMOSTAT
    }
    PUBLISH = True
    SUBSCRIBE = True


class ThermostatClient(VendorModel):
    MODEL_ID = (0x0005, 0x0001)
    OPCODE = ThermostatOpcode.VENDOR_THERMOSTAT
    SUBOPCODES = {
        ThermostatSubOpcode.THERMOSTAT_STATUS,
        ThermostatSubOpcode.THERMOSTAT_RANGE_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True

    async def get(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        return await self.client_simple_get(
            nodes=nodes,
            app_index=app_index,
            request_subopcode=ThermostatSubOpcode.THERMOSTAT_GET,
            status_subopcode=ThermostatSubOpcode.THERMOSTAT_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def set(
        self,
        nodes: Sequence[int],
        app_index: int,
        onoff: int,
        mode: int,
        temperature: float,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            onoff=onoff,
            mode=mode,
            rsvd=0,
            temperature=temperature,
            tid=self.tid(),
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_subopcode=ThermostatSubOpcode.THERMOSTAT_SET,
            status_subopcode=ThermostatSubOpcode.THERMOSTAT_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout)

    async def range_get(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        return await self.client_simple_get(
            nodes=nodes,
            app_index=app_index,
            request_subopcode=ThermostatSubOpcode.THERMOSTAT_RANGE_GET,
            status_subopcode=ThermostatSubOpcode.THERMOSTAT_RANGE_STATUS,
            send_interval=send_interval,
            timeout=timeout)
