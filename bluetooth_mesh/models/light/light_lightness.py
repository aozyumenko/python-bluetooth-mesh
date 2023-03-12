#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2019  SILVAIR sp. z o.o.
# Copyright (C) 2022  Alexander Ozumenko
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
This module implements Lighting mesh models, both clients and servers.
"""
from functools import partial
from typing import Any, Dict, Iterable, NamedTuple, Optional, Sequence, Tuple, Type

from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.generic.light.lightness import (
    LightLightnessOpcode,
    LightLightnessSetupOpcode,
)

__all__ = [
    "LightLightnessClient",
    "LightLightnessServer",
]


class LightLightnessServer(Model):
    MODEL_ID = (None, 0x1300)
    OPCODES = {
        LightLightnessOpcode.LIGHT_LIGHTNESS_GET,
        LightLightnessOpcode.LIGHT_LIGHTNESS_SET,
        LightLightnessOpcode.LIGHT_LIGHTNESS_SET_UNACKNOWLEDGED,
        LightLightnessOpcode.LIGHT_LIGHTNESS_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True


class LightLightnessSetupServer(Model):
    MODEL_ID = (None, 0x1301)
    OPCODES = {
        LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_DEFAULT_SET,
        LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_DEFAULT_SET_UNACKNOWLEDGED,
        LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_RANGE_SET,
        LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_RANGE_SET_UNACKNOWLEDGED,
    }
    SUBSCRIBE = True


class LightLightnessClient(Model):
    MODEL_ID = (None, 0x1302)
    OPCODES = {
        LightLightnessOpcode.LIGHT_LIGHTNESS_STATUS,
        LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_STATUS,
        LightLightnessOpcode.LIGHT_LIGHTNESS_LAST_STATUS,
        LightLightnessOpcode.LIGHT_LIGHTNESS_DEFAULT_STATUS,
        LightLightnessOpcode.LIGHT_LIGHTNESS_RANGE_STATUS,
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
        requests = {
            node: partial(
                self.send_app,
                destination=node,
                app_index=app_index,
                opcode=LightLightnessOpcode.LIGHT_LIGHTNESS_GET,
                params=dict(),
            )
            for node in nodes
        }

        status_opcode = LightLightnessOpcode.LIGHT_LIGHTNESS_STATUS
        statuses = {
            node: self.expect_app(
                source=node,
                app_index=app_index,
                destination=None,
                opcode=status_opcode,
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
            node: None if isinstance(result, Exception)
                    or not hasattr(result, '__getitem__')
                else result[status_opcode.name.lower()]
            for node, result in results.items()
        }


    async def set(
        self,
        nodes: Sequence[int],
        app_index: int,
        lightness: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_app,
                destination=node,
                app_index=app_index,
                opcode=LightLightnessOpcode.LIGHT_LIGHTNESS_SET,
                params=dict(
                    lightness=lightness,
                    tid=self.tid(),
                    delay=0,
                    transition_time=transition_time),
            )
            for node in nodes
        }

        status_opcode = LightLightnessOpcode.LIGHT_LIGHTNESS_STATUS
        statuses = {
            node: self.expect_app(
                source=node,
                app_index=app_index,
                destination=None,
                opcode=status_opcode,
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
            node: None if isinstance(result, Exception)
                    or not hasattr(result, '__getitem__')
                else result[status_opcode.name.lower()]
            for node, result in results.items()
        }


    async def set_unack(
        self,
        destination: int,
        app_index: int,
        lightness: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> None:
        tid = self.tid()
        remaining_delay = delay or self.UNACK_DELAY

        async def request():
            nonlocal remaining_delay
            ret = self.send_app(
                destination=destination,
                app_index=app_index,
                opcode=LightLightnessOpcode.LIGHT_LIGHTNESS_SET_UNACKNOWLEDGED,
                params=dict(
                    lightness=lightness,
                    tid=tid,
                    delay=remaining_delay,
                    transition_time=transition_time,
                )
            )
            remaining_delay = max(0.0, remaining_delay - (send_interval or self.UNACK_SEND_INTERVAL))
            return await ret

        await self.repeat(
            request,
            retransmissions=retransmissions,
            send_interval=send_interval
        )


    async def linear_get(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_app,
                destination=node,
                app_index=app_index,
                opcode=LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_GET,
                params=dict(),
            )
            for node in nodes
        }

        status_opcode = LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_STATUS
        statuses = {
            node: self.expect_app(
                source=node,
                app_index=app_index,
                destination=None,
                opcode=status_opcode,
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
            node: None if isinstance(result, Exception)
                    or not hasattr(result, '__getitem__')
                else result[status_opcode.name.lower()]
            for node, result in results.items()
        }


    async def linear_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        lightness: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_app,
                destination=node,
                app_index=app_index,
                opcode=LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_SET,
                params=dict(
                    lightness=lightness,
                    tid=self.tid(),
                    delay=0,
                    transition_time=transition_time),
            )
            for node in nodes
        }

        status_opcode = LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_STATUS
        statuses = {
            node: self.expect_app(
                source=node,
                app_index=app_index,
                destination=None,
                opcode=status_opcode,
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
            node: None if isinstance(result, Exception)
                    or not hasattr(result, '__getitem__')
                else result[status_opcode.name.lower()]
            for node, result in results.items()
        }


    async def linear_set_unack(
        self,
        destination: int,
        app_index: int,
        lightness: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> None:
        tid = self.tid()
        remaining_delay = delay or self.UNACK_DELAY

        async def request():
            nonlocal remaining_delay
            ret = self.send_app(
                destination=destination,
                app_index=app_index,
                opcode=LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_SET_UNACKNOWLEDGED,
                params=dict(
                    lightness=lightness,
                    tid=tid,
                    delay=remaining_delay,
                    transition_time=transition_time,
                )
            )
            remaining_delay = max(0.0, remaining_delay - (send_interval or self.UNACK_SEND_INTERVAL))
            return await ret

        await self.repeat(
            request,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )


    async def last_get(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_app,
                destination=node,
                app_index=app_index,
                opcode=LightLightnessOpcode.LIGHT_LIGHTNESS_LAST_GET,
                params=dict(),
            )
            for node in nodes
        }

        status_opcode = LightLightnessOpcode.LIGHT_LIGHTNESS_LAST_STATUS
        statuses = {
            node: self.expect_app(
                source=node,
                app_index=app_index,
                destination=None,
                opcode=status_opcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
            send_interval=send_interval,
            timeout=timeout or len(nodes),
        )

        return {
            node: None if isinstance(result, Exception)
                    or not hasattr(result, '__getitem__')
                else result[status_opcode.name.lower()]
            for node, result in results.items()
        }


    async def default_get(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_app,
                destination=node,
                app_index=app_index,
                opcode=LightLightnessOpcode.LIGHT_LIGHTNESS_DEFAULT_GET,
                params=dict(),
            )
            for node in nodes
        }

        status_opcode = LightLightnessOpcode.LIGHT_LIGHTNESS_DEFAULT_STATUS
        statuses = {
            node: self.expect_app(
                source=node,
                app_index=app_index,
                destination=None,
                opcode=status_opcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
            send_interval=send_interval,
            timeout=timeout or len(nodes),
        )

        return {
            node: None if isinstance(result, Exception)
                    or not hasattr(result, '__getitem__')
                else result[status_opcode.name.lower()]
            for node, result in results.items()
        }


    async def default_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        lightness: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_app,
                destination=node,
                app_index=app_index,
                opcode=LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_DEFAULT_SET,
                params=dict(
                    lightness=lightness,
                    tid=self.tid()),
            )
            for node in nodes
        }

        status_opcode = LightLightnessOpcode.LIGHT_LIGHTNESS_DEFAULT_STATUS
        statuses = {
            node: self.expect_app(
                source=node,
                app_index=app_index,
                destination=None,
                opcode=status_opcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
            send_interval=send_interval,
            timeout=timeout or len(nodes),
        )

        return {
            node: None if isinstance(result, Exception)
                    or not hasattr(result, '__getitem__')
                else result[status_opcode.name.lower()]
            for node, result in results.items()
        }


    async def default_set_unack(
        self,
        destination: int,
        app_index: int,
        lightness: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> None:
        tid = self.tid()

        async def request():
            ret = self.send_app(
                destination=destination,
                app_index=app_index,
                opcode=LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_DEFAULT_SET_UNACKNOWLEDGED,
                params=dict(
                    lightness=lightness,
                    tid=tid,
                )
            )
            return await ret

        await self.repeat(
            request,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )


    async def range_get(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> None:
        requests = {
            node: partial(
                self.send_app,
                destination=node,
                app_index=app_index,
                opcode=LightLightnessOpcode.LIGHT_LIGHTNESS_RANGE_GET,
                params=dict(),
            )
            for node in nodes
        }

        status_opcode = LightLightnessOpcode.LIGHT_LIGHTNESS_RANGE_STATUS
        statuses = {
            node: self.expect_app(
                source=node,
                app_index=app_index,
                destination=None,
                opcode=status_opcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
            send_interval=send_interval,
            timeout=timeout or len(nodes),
        )

        return {
            node: None
            if isinstance(result, Exception)
                    or not hasattr(result, '__getitem__')
                else result[status_opcode.name.lower()]
            for node, result in results.items()
        }


    async def range_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        min_lightness: int,
        max_lightness: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Optional[Any]:
        requests = {
            node: partial(
                self.send_app,
                destination=node,
                app_index=app_index,
                opcode=LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_RANGE_SET,
                params=dict(
                    range_min=min_lightness,
                    range_max=max_lightness,
                    tid=self.tid(),
                ),
            ) for node in nodes
        }

        status_opcode = LightLightnessOpcode.LIGHT_LIGHTNESS_RANGE_STATUS
        statuses = {
            node: self.expect_app(
                source=node,
                app_index=app_index,
                destination=None,
                opcode=status_opcode,
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
            node: None if isinstance(result, Exception)
                    or not hasattr(result, '__getitem__')
                else result[status_opcode.name.lower()]
            for node, result in results.items()
        }


    async def range_set_unack(
        self,
        destination: int,
        app_index: int,
        min_lightness: int,
        max_lightness: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> None:
        async def request():
            ret = self.send_app(
                destination,
                app_index=app_index,
                opcode=LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_RANGE_SET_UNACKNOWLEDGED,
                params=dict(
                    range_min=min_lightness,
                    range_max=max_lightness,
                ),
            )

            return await ret

        await self.repeat(
            request,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )
