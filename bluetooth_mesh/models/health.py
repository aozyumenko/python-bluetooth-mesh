#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2026  Alexander Ozumenko
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
This module implements Heath mesh models, both clients and servers.
"""

from typing import Any, Dict, Optional

from bluetooth_mesh.messages.health import HealthOpcode
from bluetooth_mesh.models.base import Model


__all__ = [
    "HealthServer",
    "HealthClient",
]


class HealthServer(Model):
    MODEL_ID = (None, 0x0002)
    OPCODES = {
        HealthOpcode.HEALTH_FAULT_GET,
        HealthOpcode.HEALTH_FAULT_CLEAR,
        HealthOpcode.HEALTH_FAULT_CLEAR_UNACKNOWLEDGED,
        HealthOpcode.HEALTH_FAULT_TEST,
        HealthOpcode.HEALTH_FAULT_TEST_UNACKNOWLEDGED,
        HealthOpcode.HEALTH_PERIOD_GET,
        HealthOpcode.HEALTH_PERIOD_SET,
        HealthOpcode.HEALTH_PERIOD_SET_UNACKNOWLEDGED,
        HealthOpcode.HEALTH_ATTENTION_GET,
        HealthOpcode.HEALTH_ATTENTION_SET,
        HealthOpcode.HEALTH_ATTENTION_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True


class HealthClient(Model):
    MODEL_ID = (None, 0x0003)
    OPCODES = {
        HealthOpcode.HEALTH_CURRENT_STATUS,
        HealthOpcode.HEALTH_FAULT_STATUS,
        HealthOpcode.HEALTH_PERIOD_STATUS,
        HealthOpcode.HEALTH_ATTENTION_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True

    async def fault_get(
        self,
        destination: int,
        app_index: int,
        company_id: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            company_id=company_id,
        )
        return await self.client_simple_set(
            destination=destination,
            app_index=app_index,
            request_opcode=HealthOpcode.HEALTH_FAULT_GET,
            status_opcode=HealthOpcode.HEALTH_FAULT_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def fault_clear(
        self,
        destination: int,
        app_index: int,
        company_id: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            company_id=company_id,
        )
        return await self.client_simple_set(
            destination=destination,
            app_index=app_index,
            request_opcode=HealthOpcode.HEALTH_FAULT_CLEAR,
            status_opcode=HealthOpcode.HEALTH_FAULT_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def fault_clear_unack(
        self,
        destination: int,
        app_index: int,
        company_id: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            company_id=company_id,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=HealthOpcode.HEALTH_FAULT_CLEAR_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

    async def fault_test(
        self,
        destination: int,
        app_index: int,
        test_id: int,
        company_id: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            test_id=test_id,
            company_id=company_id,
        )
        return await self.client_simple_set(
            destination=destination,
            app_index=app_index,
            request_opcode=HealthOpcode.HEALTH_FAULT_TEST,
            status_opcode=HealthOpcode.HEALTH_FAULT_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def fault_test_unack(
        self,
        destination: int,
        app_index: int,
        test_id: int,
        company_id: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            test_id=test_id,
            company_id=company_id,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=HealthOpcode.HEALTH_FAULT_TEST_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )


    async def period_get(
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
            request_opcode=HealthOpcode.HEALTH_PERIOD_GET,
            status_opcode=HealthOpcode.HEALTH_PERIOD_STATUS,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def period_set(
        self,
        destination: int,
        app_index: int,
        fast_period_divisor: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            fast_period_divisor=fast_period_divisor,
        )
        return await self.client_simple_set(
            destination=destination,
            app_index=app_index,
            request_opcode=HealthOpcode.HEALTH_PERIOD_SET,
            status_opcode=HealthOpcode.HEALTH_PERIOD_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def period_set_unack(
        self,
        destination: int,
        app_index: int,
        fast_period_divisor: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            fast_period_divisor=fast_period_divisor,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=HealthOpcode.HEALTH_PERIOD_SET_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )


    async def attention_get(
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
            request_opcode=HealthOpcode.HEALTH_ATTENTION_GET,
            status_opcode=HealthOpcode.HEALTH_ATTENTION_STATUS,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def attention_set(
        self,
        destination: int,
        app_index: int,
        attention: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            attention=attention,
        )
        return await self.client_simple_set(
            destination=destination,
            app_index=app_index,
            request_opcode=HealthOpcode.HEALTH_ATTENTION_SET,
            status_opcode=HealthOpcode.HEALTH_ATTENTION_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def attention_set_unack(
        self,
        destination: int,
        app_index: int,
        attention: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            attention=attention,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=HealthOpcode.HEALTH_ATTENTION_SET_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )
