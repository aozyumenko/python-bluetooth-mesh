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
This module implements Generic Default Transition Time mesh model, both client and server
"""
from functools import partial
from typing import Any, Dict, Iterable, NamedTuple, Optional, Tuple, Type


from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.generic.dtt import GenericDTTOpcode

__all__ = [
    "GenericDTTServer",
    "GenericDTTClient",
]


class GenericDTTServer(Model):
    MODEL_ID = (None, 0x1004)
    OPCODES = {
        GenericDTTOpcode.GENERIC_DTT_GET,
        GenericDTTOpcode.GENERIC_DTT_SET,
        GenericDTTOpcode.GENERIC_DTT_SET_UNACKNOWLEDGED,
        GenericDTTOpcode.GENERIC_DTT_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True


class GenericDTTClient(Model):
    MODEL_ID = (None, 0x1005)
    OPCODES = {
        GenericDTTOpcode.GENERIC_DTT_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True


    async def get(
        self,
        destination: int,
        app_index: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        return await self.client_simple_get(
            destination=destination,
            app_index=app_index,
            request_opcode=GenericDTTOpcode.GENERIC_DTT_GET,
            status_opcode=GenericDTTOpcode.GENERIC_DTT_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def set(
        self,
        destination: int,
        app_index: int,
        transition_time: float,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            transition_time=transition_time,
        )
        return await self.client_simple_set(
            destination=destination,
            app_index=app_index,
            request_opcode=GenericDTTOpcode.GENERIC_DTT_SET,
            status_opcode=GenericDTTOpcode.GENERIC_DTT_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def set_unack(
        self,
        destination: int,
        app_index: int,
        transition_time: float,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            transition_time=transition_time,
        )
        await self.client_simple_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=GenericDTTOpcode.GENERIC_DTT_SET_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )
