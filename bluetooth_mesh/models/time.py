#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2019  SILVAIR sp. z o.o.
# Copyright (C) 2024  Alexander Ozumenko
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
This module implements Time mesh models, both clients and servers.
"""
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.time import TimeOpcode, TimeRole


__all__ = [
    "TimeServer",
    "TimeSetupServer",
    "TimeClient",
]


class TimeServer(Model):
    MODEL_ID = (None, 0x1200)
    OPCODES = {
        TimeOpcode.TIME_GET,
        TimeOpcode.TIME_ZONE_GET,
        TimeOpcode.TAI_UTC_DELTA_GET,
    }
    PUBLISH = True
    SUBSCRIBE = True


    async def time_status(
        self,
        destination: int,
        app_index: int,
        date: datetime,
        tai_utc_delta: timedelta,
        uncertainty: timedelta,
        time_authority: bool,
    ):
        params = dict(
            date=date,
            uncertainty=uncertainty,
            time_authority=time_authority,
            tai_utc_delta=tai_utc_delta,
        )
        await self.send_app(
            destination=destination,
            app_index=app_index,
            opcode=TimeOpcode.TIME_STATUS,
            params=params,
        )

    async def time_zone_status(
        self,
        destination: int,
        app_index: int,
        time_zone_offset_current: timedelta,
        time_zone_offset_new: timedelta,
        tai_of_zone_change: int,
    ):
        params = dict(
            time_zone_offset_current=time_zone_offset_current,
            time_zone_offset_new=time_zone_offset_new,
            tai_of_zone_change=tai_of_zone_change,
        )
        await self.send_app(
            destination=destination,
            app_index=app_index,
            opcode=TimeOpcode.TIME_ZONE_STATUS,
            params=params,
        )

    async def tai_utc_delta_status(
        self,
        destination: int,
        app_index: int,
        tai_utc_delta_current: int,
        tai_utc_delta_new: int,
        tai_of_delta_change: int,
    ):
        params = dict(
            tai_utc_delta_current=tai_utc_delta_current,
            tai_utc_delta_new=tai_utc_delta_new,
            tai_of_delta_change=tai_of_delta_change,
        )
        await self.send_app(
            destination=destination,
            app_index=app_index,
            opcode=TimeOpcode.TAI_UTC_DELTA_STATUS,
            params=params,
        )


class TimeSetupServer(Model):
    MODEL_ID = (None, 0x1201)
    OPCODES = {
        TimeOpcode.TIME_SET,
        TimeOpcode.TIME_ZONE_SET,
        TimeOpcode.TAI_UTC_DELTA_SET,
        TimeOpcode.TIME_ROLE_SET,
        TimeOpcode.TIME_ROLE_GET,
    }
    PUBLISH = False
    SUBSCRIBE = False

    async def time_role_status(
        self,
        destination: int,
        app_index: int,
        time_role: TimeRole,
    ):
        params = dict(time_role=time_role)
        await self.send_app(
            destination=destination,
            app_index=app_index,
            opcode=TimeOpcode.TIME_ROLE_STATUS,
            params=params,
        )


class TimeClient(Model):
    MODEL_ID = (None, 0x1202)
    OPCODES = {
        TimeOpcode.TIME_STATUS,
        TimeOpcode.TIME_ZONE_STATUS,
        TimeOpcode.TAI_UTC_DELTA_STATUS,
        TimeOpcode.TIME_ROLE_STATUS,
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
            request_opcode=TimeOpcode.TIME_GET,
            status_opcode=TimeOpcode.TIME_STATUS,
            send_interval=send_interval,
            timeout=timeout,
        )


    async def time_zone_get(
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
            request_opcode=TimeOpcode.TIME_ZONE_GET,
            status_opcode=TimeOpcode.TIME_ZONE_STATUS,
            send_interval=send_interval,
            timeout=timeout,
        )


    async def tai_utc_delta_get(
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
            request_opcode=TimeOpcode.TAI_UTC_DELTA_GET,
            status_opcode=TimeOpcode.TAI_UTC_DELTA_STATUS,
            send_interval=send_interval,
            timeout=timeout,
        )


    async def set(
        self,
        destination: int,
        app_index: int,
        date: datetime,
        tai_utc_delta: timedelta,
        uncertainty: timedelta,
        time_authority: bool,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            date=date,
            uncertainty=uncertainty,
            time_authority=time_authority,
            tai_utc_delta=tai_utc_delta,
        )
        return await self.client_simple_set(
            destination=destination,
            app_index=app_index,
            request_opcode=TimeOpcode.TIME_SET,
            status_opcode=TimeOpcode.TIME_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )


    async def time_zone_set(
        self,
        destination: int,
        app_index: int,
        time_zone_offset_current: timedelta,
        time_zone_offset_new: timedelta,
        tai_of_zone_change: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            time_zone_offset_current=time_zone_offset_current,
            time_zone_offset_new=time_zone_offset_new,
            tai_of_zone_change=tai_of_zone_change,
        )
        return await self.client_simple_set(
            destination=destination,
            app_index=app_index,
            request_opcode=TimeOpcode.TIME_ZONE_SET,
            status_opcode=TimeOpcode.TIME_ZONE_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )


    async def tai_utc_delta_set(
        self,
        destination: int,
        app_index: int,
        tai_utc_delta_current: int,
        tai_utc_delta_new: int,
        tai_of_delta_change: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            tai_utc_delta_current=tai_utc_delta_current,
            tai_utc_delta_new=tai_utc_delta_new,
            tai_of_delta_change=tai_of_delta_change,
        )
        return await self.client_simple_set(
            destination=destination,
            app_index=app_index,
            request_opcode=TimeOpcode.TAI_UTC_DELTA_SET,
            status_opcode=TimeOpcode.TAI_UTC_DELTA_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )


    async def time_role_get(
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
            request_opcode=TimeOpcode.TIME_ROLE_GET,
            status_opcode=TimeOpcode.TIME_ROLE_STATUS,
            send_interval=send_interval,
            timeout=timeout,
        )


    async def time_role_set(
        self,
        destination: int,
        app_index: int,
        time_role: TimeRole,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ):
        params=dict(time_role=time_role)
        return await self.client_simple_set(
            destination=destination,
            app_index=app_index,
            request_opcode=TimeOpcode.TIME_ROLE_SET,
            status_opcode=TimeOpcode.TIME_ROLE_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )
