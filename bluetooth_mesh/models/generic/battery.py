#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2025  Alexander Ozumenko
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
This module implements GenericBattery mesh model, both client and server
"""
from functools import partial
from typing import Any, Dict, Iterable, NamedTuple, Optional, Sequence, Tuple, Type

from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.generic.battery import GenericBatteryOpcode

__all__ = [
    "GenericBatteryServer",
    "GenericBatteryClient",
]



class GenericBatteryServer(Model):
    MODEL_ID = (None, 0x100c)
    OPCODES = {
        GenericBatteryOpcode.GENERIC_BATTERY_GET,
    }
    PUBLISH = True
    SUBSCRIBE = True


class GenericBatteryClient(Model):
    MODEL_ID = (None, 0x100d)
    OPCODES = {
        GenericBatteryOpcode.GENERIC_BATTERY_STATUS,
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
            request_opcode=GenericBatteryOpcode.GENERIC_BATTERY_GET,
            status_opcode=GenericBatteryOpcode.GENERIC_BATTERY_STATUS,
            send_interval=send_interval,
            timeout=timeout)
