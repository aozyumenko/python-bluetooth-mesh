from construct import Select

from .level import GenericLevelMessage
from .onoff import GenericOnOffMessage
from .dtt import GenericDTTMessage
from .ponoff import  GenericPowerOnOffMessage, GenericPowerOnOffSetupMessage
from .battery import  GenericBatteryMessage

GenericMessage = Select(
    GenericOnOffMessage,
    GenericLevelMessage,
    GenericDTTMessage,
    GenericPowerOnOffMessage,
    GenericPowerOnOffSetupMessage,
    GenericBatteryMessage,
)
