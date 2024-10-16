#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2019  SILVAIR sp. z o.o.
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
import pytest

from bluetooth_mesh.messages.config import StatusCode
from bluetooth_mesh.messages.vendor.thermostat import (
    ThermostatMessage,
    ThermostatOpcode,
    ThermostatSubOpcode,
    ThermostatStatusCode,
    ThermostatMode,
)

valid_thermostat = [
    pytest.param(
        b'\xc0\x05\x00\x00',
        ThermostatSubOpcode.THERMOSTAT_GET,
        dict(),
        id="THERMOSTAT_GET"
    ),
    pytest.param(
        b'\xc0\x05\x00\x01\x00Z\n',
        ThermostatSubOpcode.THERMOSTAT_SET,
        dict(
            rsvd = 0,
            mode = ThermostatMode.MANUAL,
            temperature = 26.5,
        ),
        id="THERMOSTAT_SET"
    ),
    pytest.param(
        b'\xc0\x05\x00\x02\x00\tZ\n\x10\xfa',
        ThermostatSubOpcode.THERMOSTAT_STATUS,
        dict(
            status_code = ThermostatStatusCode.GOOD,
            rsvd = 0,
            heater_status = True,
            mode = ThermostatMode.MANUAL,
            onoff_status = True,
            target_temperature = 26.5,
            present_temperature = -15.2,
        ),
        id="THERMOSTAT_STATUS"
    ),
    pytest.param(
        b'\xc0\x05\x00\x03',
        ThermostatSubOpcode.THERMOSTAT_RANGE_GET,
        dict(),
        id="THERMOSTAT_RANGE_GET"
    ),
    pytest.param(
        b'\xc0\x05\x00\x040\xf8\xa0\x0f',
        ThermostatSubOpcode.THERMOSTAT_RANGE_STATUS,
        dict(
            min_temperature = -20,
            max_temperature = 40,
        ),
        id="THERMOSTAT_RANGE_STATUS"
    ),
]


@pytest.mark.parametrize("encoded,subopcode,data", valid_thermostat)
def test_parse_valid_thermostat(encoded, subopcode, data):
    assert ThermostatMessage.parse(encoded).params.payload == data

@pytest.mark.parametrize("encoded,subopcode,data", valid_thermostat)
def test_build_valid_thermostat(encoded, subopcode, data):
    assert ThermostatMessage.build(dict(opcode=ThermostatOpcode.THERMOSTAT, params=dict(subopcode=subopcode, payload=data))) == encoded
