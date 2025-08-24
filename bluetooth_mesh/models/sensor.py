#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2019  SILVAIR sp. z o.o.
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
This module implements Sensor mesh models, both clients and servers.
"""
from functools import partial
from typing import Any, Dict, Iterable, NamedTuple, Optional, Union, Tuple, Type

from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.sensor import SensorOpcode, SensorSetupOpcode
from bluetooth_mesh.messages.properties import PropertyID


__all__ = [
    "SensorServer",
    "SensorSetupServer",
    "SensorClient",
]


class SensorServer(Model):
    MODEL_ID = (None, 0x1100)
    OPCODES = {
        SensorOpcode.SENSOR_DESCRIPTOR_GET,
        SensorOpcode.SENSOR_GET,
        # SensorOpcode.SENSOR_COLUMN_GET,
        # SensorOpcode.SENSOR_SERIES_GET,
    }
    PUBLISH = True
    SUBSCRIBE = True


class SensorSetupServer(Model):
    MODEL_ID = (None, 0x1101)
    OPCODES = {
        SensorSetupOpcode.SENSOR_CADENCE_GET,
        SensorSetupOpcode.SENSOR_CADENCE_SET,
        SensorSetupOpcode.SENSOR_CADENCE_SET_UNACKNOWLEDGED,
        SensorSetupOpcode.SENSOR_SETTINGS_GET,
        SensorSetupOpcode.SENSOR_SETTING_GET,
        SensorSetupOpcode.SENSOR_SETTING_SET,
        SensorSetupOpcode.SENSOR_SETTING_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True


class SensorClient(Model):
    MODEL_ID = (None, 0x1102)
    OPCODES = {
        SensorOpcode.SENSOR_DESCRIPTOR_STATUS,
        SensorOpcode.SENSOR_STATUS,
        # SensorOpcode.SENSOR_COLUMN_STATUS,
        # SensorOpcode.SENSOR_SERIES_STATUS,
        SensorSetupOpcode.SENSOR_CADENCE_STATUS,
        SensorSetupOpcode.SENSOR_SETTINGS_STATUS,
        SensorSetupOpcode.SENSOR_SETTING_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True

    async def descriptor_get(
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
            request_opcode=SensorOpcode.SENSOR_DESCRIPTOR_GET,
            status_opcode=SensorOpcode.SENSOR_DESCRIPTOR_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def cadence_get(
        self,
        destination: int,
        app_index: int,
        property_id: Optional[PropertyID] = None,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        request = partial(
            self.send_app,
            destination,
            app_index=app_index,
            opcode=SensorSetupOpcode.SENSOR_CADENCE_GET,
            params=dict(property_id=property_id),
        )

        status_opcode = SensorSetupOpcode.SENSOR_CADENCE_STATUS
        status = self.expect_app(
            destination,
            app_index=0,
            destination=None,
            opcode=status_opcode,
            params=dict(),
        )

        result = await self.query(
            request,
            status,
            send_interval=send_interval,
            timeout=timeout,
        )

        return None if isinstance(result, BaseException) else result[status_opcode.name.lower()]


    async def cadence_set(
        self,
        destination: int,
        app_index: int,
        sensor_setting_property_id: PropertyID,
        fast_cadence_period_divisor: int,
        status_trigger_type: int,
        status_trigger_delta_down: Union[dict, float],
        status_trigger_delta_up: Union[dict, float],
        status_min_interval: int,
        fast_cadence_low: Union[dict, float],
        fast_cadence_high: Union[dict, float],
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params=dict(
            sensor_setting_property_id=sensor_setting_property_id,
            fast_cadence_period_divisor=fast_cadence_period_divisor,
            status_trigger_type=status_trigger_type,
            status_trigger_delta_down=status_trigger_delta_down,
            status_trigger_delta_up=status_trigger_delta_up,
            status_min_interval=status_min_interval,
            fast_cadence_low=fast_cadence_low,
            fast_cadence_high=fast_cadence_high,
        )
        return await self.client_simple_set(
            destination=destination,
            app_index=app_index,
            request_opcode=SensorSetupOpcode.SENSOR_CADENCE_SET,
            status_opcode=SensorSetupOpcode.SENSOR_CADENCE_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )


    async def get(
        self,
        destination: int,
        app_index: int,
        *,
        property_id: Optional[PropertyID] = None,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        request = partial(
            self.send_app,
            destination,
            app_index=app_index,
            opcode=SensorOpcode.SENSOR_GET,
            params=dict(property_id=property_id),
        )

        status_opcode = SensorOpcode.SENSOR_STATUS
        status = self.expect_app(
            destination,
            app_index=0,
            destination=None,
            opcode=status_opcode,
            params=dict(),
        )

        result = await self.query(
            request,
            status,
            send_interval=send_interval,
            timeout=timeout,
        )

        return None if isinstance(result, BaseException) else result[status_opcode.name.lower()]
