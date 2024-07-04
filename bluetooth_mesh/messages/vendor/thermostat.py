#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2024 Alexander Ozumenko
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
from enum import IntEnum
from construct import (
    Int8ul,
    Int16sl,
    Struct,
    Flag,
    BitsInteger,
    Switch,
    this,
)

from bluetooth_mesh.messages.util import EnumAdapter
from bluetooth_mesh.messages.util import NamedSelect, Opcode, SwitchStruct
from bluetooth_mesh.messages.config import EmbeddedBitStruct
from bluetooth_mesh.messages.properties import DefaultCountValidator

# NOTE: VID=0x0005 is only used for testing and should be changed in the future
class ThermostatOpcode(IntEnum):
    THERMOSTAT = 0xC00500

class ThermostatSubOpcode(IntEnum):
    THERMOSTAT_GET = 0x00
    THERMOSTAT_SET = 0x01
    THERMOSTAT_STATUS = 0x02
    THERMOSTAT_RANGE_GET = 0x03
    THERMOSTAT_RANGE_STATUS = 0x04

class ThermostatStatusCode(IntEnum):
    GOOD = 0x00
    INVALID_MODE = 0x01
    INVALID_TEMPERATURE = 0x02

class ThermostatMode(IntEnum):
    MANUAL = 0x0
    AUTO = 0x1
    RSVD1 = 0x2
    RSVD2 = 0x3

# temperature
Temperature = DefaultCountValidator(Int16sl, rounding=2, resolution=0.01)


ThermostatGet = Struct()

ThermostatSet = Struct(
    *EmbeddedBitStruct("_",
        "rsvd" / BitsInteger(6),
        "mode" / EnumAdapter(BitsInteger(2), ThermostatMode),
    ),
    "temperature" / Temperature,
)

ThermostatStatus = Struct(
    "status_code" / EnumAdapter(Int8ul, ThermostatStatusCode),
    *EmbeddedBitStruct("_",
        "rsvd" / BitsInteger(4),
        "heater_status" / Flag,
        "mode" / EnumAdapter(BitsInteger(2), ThermostatMode),
        "onoff_status" / Flag,
    ),
    "target_temperature" / Temperature,
    "present_temperature" / Temperature,
)

ThermostatRangeGet = Struct()

ThermostatRangeStatus = Struct(
    "min_temperature" / Temperature,
    "max_temperature" / Temperature,
)


ThermostatParams = SwitchStruct(
    "subopcode" / EnumAdapter(Int8ul, ThermostatSubOpcode),
    "payload" / Switch(
        this.subopcode,
        {
            ThermostatSubOpcode.THERMOSTAT_GET: ThermostatGet,
            ThermostatSubOpcode.THERMOSTAT_SET: ThermostatSet,
            ThermostatSubOpcode.THERMOSTAT_STATUS: ThermostatStatus,
            ThermostatSubOpcode.THERMOSTAT_RANGE_GET: ThermostatRangeGet,
            ThermostatSubOpcode.THERMOSTAT_RANGE_STATUS: ThermostatRangeStatus,
        },
    ),
)

ThermostatMessage = SwitchStruct(
    "opcode" / Opcode(ThermostatOpcode),
    "params" / Switch(
        this.opcode,
        {
            ThermostatOpcode.THERMOSTAT: ThermostatParams
        },
    ),
)
